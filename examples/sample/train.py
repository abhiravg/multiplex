import os
import sys
import argparse

from multiplex.parser import Multiplexor
from multiplex import register_parser, register_entrypoint
from multiplex.config import DotListConfig
from multiplex.utils import to_nested_dict

@register_entrypoint
def main(args):
    
    m = Multiplexor('C:/Users/Rocil/eclipse-workspace/multiplex/examples/sample/train.yaml')
    parser_train = m.get_parser()
    main_args, train_args = parser_train.parse_known_args()
    unknown_args_dict = get_subprogram_args(train_args)
    unknown_args_dict = to_nested_dict(unknown_args_dict)
    print(unknown_args_dict)
    
    for key, value in unknown_args_dict.items():
        file_dir_name = key + '.yaml'
        if(os.path.isfile(file_dir_name)):  #Returns true if file, false if AdjacentTempDirectory
            m1 = Multiplexor(file_dir_name)
            final_conf = m1.full_config + DotListConfig(value)
            print(final_conf)
                    
def get_subprogram_args(train_args):
    unknown_args_dict = {}
    for arg in train_args:
        if arg.startswith('--programs'):
            continue
        params = arg.split("=")
        if(params[0].startswith("--")):
            unknown_args_dict.setdefault(params[0][2:], params[1])
    return unknown_args_dict




    