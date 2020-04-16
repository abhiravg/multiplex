import os
from copy import deepcopy

import argparse
import builtins

from multiplex.config import DotListConfig


class Multiplexor:
    def __init__(self, config_or_path, argparse_key='argparse', dotlist_sep='.'):
        if issubclass(type(config_or_path), DotListConfig):
            self.full_config = config_or_path
        elif issubclass(type(config_or_path), dict):
            self.full_config = DotListConfig(config_or_path)
        elif issubclass(type(config_or_path), str):
            if os.path.exists(config_or_path):
                self.full_config = DotListConfig.from_path(config_or_path)
            else:
                self.full_config = DotListConfig.from_text(config_or_path, 'yaml')
        else:
            raise ValueError("Config needs to be either: a path to a valid config,"
                             "a dictionary or DotListConfig object, or a string.")

        self.dotlist_sep, self.argparse_key = dotlist_sep, argparse_key

    @staticmethod
    def get_type_from_str(type_name):
        # TODO: Not safe, this can execute eval
        return getattr(builtins, type_name)

    def to_nested_dict(self, d):
        new = {}

        def add_element(key, value):
            if self.dotlist_sep in key:
                subdict = new
                for part in key.split(self.dotlist_sep)[:-1]:
                    if part not in subdict:
                        subdict[part] = {}
                    subdict = subdict[part]
                subdict[key.split(self.dotlist_sep)[-1]] = value
            else:
                new[key] = value

        for key, value in d.items():
            add_element(key, value)
        return new

    def get_parser(self, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        parser = self.add_arparse_arguments(parser)
        parser = self.add_default_arguments(parser)
        return parser

    def get_cli_conf(self, parser=None, args=None, namespace=None):
        parser = self.get_parser(parser)
        cli_conf = vars(parser.parse_args(args, namespace))
        cli_conf = self.to_nested_dict(cli_conf)
        return DotListConfig(cli_conf)

    def get_default_conf(self):
        data = deepcopy(self.full_config.data)
        if isinstance(data, dict):
            data.pop(self.argparse_key, [])
        return DotListConfig(data)

    def get_conf(self, *args, **kwargs):
        return self.get_default_conf() + self.get_cli_conf(*args, **kwargs)

    def add_default_arguments(self, parser):
        group = parser.add_argument_group('default parameters')
        for arg in self.full_config.keys():
            if arg.startswith(self.argparse_key):
                continue
            arg_name = f'--{arg.replace(" ", "_")}'
            value = self.full_config[arg]
            group.add_argument(arg_name, default=value, dest=arg,
                               help=f"default is {repr(value)}", metavar='')
        return parser

    def add_arparse_arguments(self, parser):
        allowed_keys = {"name_or_flags", "action", "nargs", "const", "default",
                        "type", "choices", "required", "help", "metavar", "dest"}
        required_keys = {"name_or_flags"}

        for arg_def in self.full_config.data.get(self.argparse_key, []):
            # Validate fields of argparse add_argument
            extra_keys = arg_def.keys() - allowed_keys
            missing_keys = required_keys - arg_def.keys()
            if missing_keys:
                raise ValueError(f'Missing required argparse keyword arguments: {missing_keys}')
            if extra_keys:
                raise ValueError(f'Unrecognized argparse keyword arguments: {extra_keys}')

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


# parser = argparse.ArgumentParser()
# m = Multiplexor('config.yaml')
# args = m.get_conf()
#
# print(args)
