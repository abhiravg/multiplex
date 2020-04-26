import builtins
import argparse

from .config import DotListConfig

# Note: Currently only argparse is supported, other CLI engines could be added here.


class ArgparseEngine:
    """This class takes in the part of a config file that explicitly specifies
    how to construct an argparse parser and generates it.

    It does this in a two step approach:
        1) Create the parser object based on metadata indicated by the `parser_key`
        2) Add arguments to this parser based on metadata under the `args_key`
    """
    allowed_keys = {
        "ArgumentParser": {'prog', 'usage', 'description', 'epilog', 'parents',
                           'formatter_class', 'prefix_chars', 'fromfile_prefix_chars',
                           'argument_default', 'conflict_handler', 'add_help', 'allow_abbrev'},
        "add_argument": {"name_or_flags", "action", "nargs", "const", "default",
                         "type", "choices", "required", "help", "metavar", "dest"}
    }

    required_keys = {
        "ArgumentParser": set(), "add_argument": {"name_or_flags"}
    }

    unsupported_keys = {
        "ArgumentParser": {'parents', 'formatter_class', 'conflict_handler'},
        "add_argument": set()
    }

    def __init__(self, argparse_conf, parser_key='parser', args_key='arguments'):
        self.argparse_conf = argparse_conf
        self.parser_key, self.args_key = parser_key, args_key
        self.parser_conf = DotListConfig(self.argparse_conf.get(self.parser_key))
        self.args_conf = DotListConfig(self.argparse_conf.get(self.args_key))

    @staticmethod
    def get_type_from_str(type_name):
        # TODO: Not safe, this can execute eval
        return getattr(builtins, type_name)

    def validate_fields(self, args, method_type):
        args = DotListConfig(args)
        extra_keys = set(args.keys()) - self.allowed_keys[method_type]
        missing_keys = self.required_keys[method_type] - set(args.keys())
        disallowed_keys = set(args.keys()) & self.unsupported_keys[method_type]

        if missing_keys:
            raise ValueError(f'Missing required argparse keyword arguments: {missing_keys}')
        if extra_keys:
            raise ValueError(f'Unrecognized argparse keyword arguments: {extra_keys}')
        if disallowed_keys:
            raise NotImplementedError(f'Some argparse keyword arguments not implemented yet: {disallowed_keys}')

    def get_parser(self):
        parser = self.get_emtpy_parser()
        parser = self.add_argparse_arguments(parser)
        return parser

    def get_emtpy_parser(self, parents=None, add_help=True):
        """Perform step 1 from above, that is, create the emtpy parser object"""
        parents = [] if parents is None else parents

        if self.parser_key not in self.argparse_conf:
            return argparse.ArgumentParser(parents=parents, add_help=add_help)

        # Validate fields of argparse ArgumentParser
        self.validate_fields(self.parser_conf, 'ArgumentParser')

        # Force remove help
        if not add_help:
            self.parser_conf.data.update({'add_help': False})

        return argparse.ArgumentParser(**self.parser_conf.data, parents=parents)

    def add_argparse_arguments(self, parser, args_conf=None, add_help=True):
        """Performs step 2, add arguments to the created parser.

        If add_help is false, capture the argument definition that have a
        help action and return these as well as the parser."""

        help_arg_defs = []
        if args_conf is None:
            args_conf = self.args_conf.data
        for arg_def in args_conf:
            # Validate fields of argparse add_argument
            self.validate_fields(arg_def, 'add_argument')

            # Find names arguments, single if positional, multiple if optional
            name_or_flags = arg_def.pop('name_or_flags')
            if issubclass(type(name_or_flags), (tuple, list)):
                names = list(name_or_flags)
                is_positional = len(name_or_flags) == 1
            else:
                names = [name_or_flags]
                is_positional = True

            # Transform any other parameters like type
            if 'type' in arg_def:
                arg_def['type'] = self.get_type_from_str(arg_def['type'])

            # Add argument to parser (or skip if not add_help)
            if not add_help and not is_positional and arg_def.get('action') == 'help':
                help_arg_defs.append(arg_def)
            else:
                parser.add_argument(*names, **arg_def)
        if not add_help:
            return parser, help_arg_defs
        return parser

