import os
from copy import deepcopy

import argparse

from .config import DotListConfig
from .engines import ArgparseEngine
from .utils import to_nested_dict


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
        self.default_conf, self.argparse_conf = self.split_conf()

    def split_conf(self):
        data = deepcopy(self.full_config.data)
        if isinstance(data, dict):
            argparse_conf = data.pop(self.argparse_key, [])
        else:
            argparse_conf = None
        default_conf = DotListConfig(data)
        return default_conf, argparse_conf

    def get_parser(self, parser=None):
        if self.argparse_conf:
            argparse_engine = ArgparseEngine(self.argparse_conf)
            parser = argparse_engine.get_parser()
        if parser is None:
            parser = argparse.ArgumentParser()
        parser = self.add_default_arguments(parser)
        return parser

    def get_subprogram_args(self,subprogram_args):
        subprogram_args_dict = {}
        for arg in subprogram_args:
#             if arg.startswith('--programs'):
#                 continue
            params = arg.split("=")
            if(params[0].startswith("--")):
                subprogram_args_dict.setdefault(params[0][2:], params[1])
        return subprogram_args_dict

#     def nested_conf(self, subprogram_args_dict):
#         nested_conf = {}
#         for i in range (0, len(subprogram_args_dict)):
#             nested_conf = nested_conf + self.get_nested_config(subprogram_args_dict[i])
#         return nested_conf


    def get_nested_config(self,subprogram_args_dict):
        for key, value in subprogram_args_dict.items():
            file_dir_name = os.path.abspath(key)
            file_name = file_dir_name + '.yaml'
            if(os.path.isfile(file_name)):  #Returns true if file
                m1 = Multiplexor(file_name)
                final_conf = m1.full_config + DotListConfig(value)
                return DotListConfig(final_conf)
            elif(os.path.isdir(file_dir_name)):
                curr_dir = os.getcwd()
                os.chdir(file_dir_name)
                #file_name = file_dir_name +'\\'+ list(value.keys())[0]+'.yaml'
                final_conf = self.get_nested_config(value)
                os.chdir(curr_dir)
                return DotListConfig(final_conf)

    def get_cli_conf(self, parser=None, args=None, namespace=None):
        parser = self.get_parser(parser)
        cli_conf, unknown_args = parser.parse_known_args(args, namespace)
        cli_conf = vars(cli_conf)
        unknown_args = self.get_subprogram_args(unknown_args)
        unknown_args = to_nested_dict(unknown_args)
        #cli_conf = vars(parser.parse_args(args, namespace))
        cli_conf = to_nested_dict(cli_conf)
        return DotListConfig(cli_conf), unknown_args

    def get_conf(self, *args, **kwargs):
        cli_conf, unknown_args = self.get_cli_conf(*args, **kwargs)
        return (self.default_conf + cli_conf),unknown_args
        #return (self.default_conf + self.get_cli_conf(*args, **kwargs))

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

#   def list_commands(self):
#         rv = []
#         self.get_cli_conf()
#         program_name = args.data.get('programs')
#         if program_name.endswith('.py'):
#                 #rv.append(program_name[:-3])
#             rv.append(program_name)
#         #rv.sort
#         return rv

    def run_command(self, args):
        program_file = args.data.get('programs')
        with open(program_file) as f:
            code = compile(f.read(), program_file, 'exec')
            eval(code, args.data)
        return

# parser = argparse.ArgumentParser()
# m = Multiplexor('config.yaml')
# args = m.get_conf()
#
# print(args)
