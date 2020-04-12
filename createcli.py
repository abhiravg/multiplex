import sys
import builtins
import argparse

from configurator import Config
from ruamel.yaml import YAML


def get_type_from_str(type_name):
    # TODO: Not safe, this can execute eval
    return getattr(builtins, type_name)


def load_conf(config_path):
    # with open(config_path, 'r') as f:
    #     yaml = YAML()
    #     return yaml.load(f)
    return Config.from_path(config_path)


def arguments_from_yaml(config_path, parser=None, argparse_key='argparse'):
    allowed_keys = {"name_or_flags", "action", "nargs", "const", "default",
                    "type", "choices", "required", "help", "metavar", "dest"}
    required_keys = {"name_or_flags"}

    config = load_conf(config_path)

    if parser is None:
        parser = argparse.ArgumentParser()

    for arg_def in config.data.pop(argparse_key, []):
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
            arg_def['type'] = get_type_from_str(arg_def['type'])

        # Add argument to parser
        parser.add_argument(*names, **arg_def)

    return parser, config


parser = argparse.ArgumentParser()
parser, base_config = arguments_from_yaml('config.yaml', parser=parser)
args = Config(vars(parser.parse_args(namespace=None)))
config = base_config + args

print(config)

# parser.add_argument('config_path', type=str, nargs='?', default='config.yaml',
#                     help='configuration file path, expected py file with a conf dictionary')
# args, argv = parser.parse_known_args()
