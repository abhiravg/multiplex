import argparse
from copy import deepcopy

from .config import DotListConfig
from .engines import ArgparseEngine
from .utils import *


class Multiplexor:
    def __init__(self, config_or_path, argparse_key='argparse', subprogram_key='subprograms', dotlist_sep='.'):
        if issubclass(type(config_or_path), DotListConfig):
            self.full_config = config_or_path
        elif issubclass(type(config_or_path), dict):
            self.full_config = DotListConfig(config_or_path)
        elif issubclass(type(config_or_path), str):
            for ext in ('yaml', 'json'):
                base_path, _ = os.path.splitext(config_or_path)
                augmented_path = base_path + os.path.extsep + ext
                if os.path.isfile(augmented_path):
                    self.full_config = DotListConfig.from_path(augmented_path)
                    break
            else:
                self.full_config = DotListConfig.from_text(config_or_path, 'yaml')
        else:
            raise ValueError("Config needs to be either: a path to a valid config,"
                             "a dictionary or DotListConfig object, or a string.")

        self.dotlist_sep = dotlist_sep
        self.argparse_key, self.subprogram_key = argparse_key, subprogram_key
        self.default_conf, self.argparse_conf, self.subprogram_conf = self._split_conf()

    def _split_conf(self):
        """Split full config into it's parts:
            - the default config
            - the argparse config
            - the subprogram config

        Returns:
            the three configs
        """
        data = deepcopy(self.full_config.data)
        if isinstance(data, dict):
            argparse_conf = data.pop(self.argparse_key, [])
            subprogram_conf = data.pop(self.subprogram_key, [])
        else:
            argparse_conf, subprogram_conf = None, None
        default_conf = DotListConfig(data)
        argparse_conf = DotListConfig(argparse_conf)
        subprogram_conf = DotListConfig(subprogram_conf)
        return default_conf, argparse_conf, subprogram_conf

    def parse_args(self):
        """Generate CLI parser based on config, and parse it's args.

        This method either simply creates and executes the main program's
        parser, or if any, will spawn the corresponding parser of a
        subprogram as they are invoked. This sub-parser will inherit from
        the main parser (with the exception of the subprogram argument).

        Returns:
            (tuple): tuple containing:
                - the parsed arguments (as a namespace)
                - the subprogram as a module, or None if main program
        """
        if self.subprogram_conf.data:
            # TODO: Add default args, i.e: the ones not in 'argparse'

            # Get shared args (everything except help)
            shared_parser = argparse.ArgumentParser(add_help=False)
            argparse_engine = ArgparseEngine(self.argparse_conf)
            shared_parser, help_args = argparse_engine.add_argparse_arguments(add_help=False, parser=shared_parser)

            # Get exclusive args (only the subprogram arg)
            exclusive_parser = argparse.ArgumentParser(add_help=False)
            subprogram_group = exclusive_parser.add_argument_group(self.subprogram_key)
            subprogram_group.add_argument('program', nargs='?', choices=self.subprogram_conf.data.keys())

            # Get main parser (without help)
            main_parser = argparse_engine.get_emtpy_parser(add_help=False, parents=[exclusive_parser, shared_parser])

            # Parse only known arguments, capturing unknown ones for downstream processing
            args, unknown_args = main_parser.parse_known_args()

            # If a subprogram is selected, import it (by full path), run it's parser and pass the
            # main parser as a parent parser, then call it's entry point
            if args.program:
                program_path = self.subprogram_conf[args.program].data
                program_path = os.path.abspath(program_path)
                subprogram = import_from_full_path(program_path)
                subparser = get_parser_from_module(subprogram, parents=[shared_parser])

                # Fix name of subparser, remove program from args
                subparser.prog = main_parser.prog + ' ' + args.program
                args = argparse.Namespace(**{k: v for k, v in vars(args).items() if k != 'program'})

                args = subparser.parse_args(args=unknown_args, namespace=args)
                return args, subprogram

            # Otherwise, add help and re-parse all arguments of main program in order to generate
            # all the correct errors if unknown arguments are present.
            else:
                main_parser.add_argument("-h", "--help", action="help", help="show this help message and exit")
                return main_parser.parse_args(), None
        else:
            # No subprograms, proceed normally
            parser = self._get_main_parser()
            return parser.parse_args(), None

    def execute(self):
        # TODO: this is currently passing the args as a Namespace. We need to
        #  merge this with default params and pass the args as a config object.
        args, subprogram = self.parse_args()
        entry_point = get_entrypoint_from_module(subprogram)
        entry_point(args)

    def get_parser(self, parents=None):
        """This method is intended to get the parser of the final subprogram,
        it raises an error if the config has a `subprogram` config"""
        if self.subprogram_conf.data:
            raise RuntimeError("Can only get parser of leaf program")
        return self._get_main_parser(self, parents=parents)

    def _get_main_parser(self, parser=None, parents=None):
        if self.argparse_conf.data:
            argparse_engine = ArgparseEngine(self.argparse_conf)
            parser = argparse_engine.get_parser(parents=parents)
        if parser is None:
            parents = [] if parents is None else parents
            parser = argparse.ArgumentParser(parents=parents)
        parser = self.add_default_arguments(parser)
        return parser

    def get_cli_conf(self, parser=None, args=None, namespace=None):
        parser = self._get_main_parser(parser)
        cli_conf = vars(parser.parse_args(args, namespace))
        cli_conf = to_nested_dict(cli_conf)
        return DotListConfig(cli_conf)

    def get_conf(self, *args, **kwargs):
        return self.default_conf + self.get_cli_conf(*args, **kwargs)

    def add_default_arguments(self, parser):
        group = parser.add_argument_group('default parameters')
        for arg in self.default_conf.keys():
            arg_name = f'--{arg.replace(" ", "_")}'
            value = self.full_config[arg]
            group.add_argument(arg_name, default=value, dest=arg,
                               help=f"default is {repr(value.data)}", metavar='')
        return parser
