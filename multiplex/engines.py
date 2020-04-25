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

    def get_emtpy_parser(self):
        """Perform step 1 from above, that is, create the emtpy parser object"""
        if self.parser_key not in self.argparse_conf:
            return argparse.ArgumentParser()

        # Validate fields of argparse ArgumentParser
        self.validate_fields(self.parser_conf, 'ArgumentParser')

        return argparse.ArgumentParser(**self.parser_conf.data)

    def add_argparse_arguments(self, parser):
        """Performs step 2, add arguments to the created parser"""
        for arg_def in self.args_conf.data:
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

            # Add argument to parser
            parser.add_argument(*names, **arg_def)
        return parser

