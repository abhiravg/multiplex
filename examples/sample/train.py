import os
import sys
import argparse

from multiplex import Multiplexor
from multiplex import register_parser, register_entrypoint
from multiplex import DotListConfig
from multiplex import to_nested_dict
from multiplex import import_from_full_path, get_parser_from_module, get_entrypoint_from_module

#subprogram_args :These are the config args passed by the main program, these couldnt be parsed by the main program's config file
#train_args : These are the arguments that are parsed successfully by the subprogram's config file
#unknown_args : These are the arguments that couldnt be parsed by the subprogram's config. In addition to
#               the nested configs, this can also contain args parsed succesfully by the main program(ignore them)


@register_entrypoint
def main(args, subprogram_args):
    
    m = Multiplexor('C:/Users/Rocil/eclipse-workspace/multiplex/examples/sample/train.yaml')
    train_args, unknown_args = m.get_conf()
    
    print("Args passed to the subprogram from the main program: ", subprogram_args)  
    print("Args parsed from the subprogram config file: ", train_args)  #Subprogram config
    
    #TODO : If any of the subprogram_args are present in train_args, remove them from subprogram_args
    
    
    print("Args unparsed from the subprogram config file: ", unknown_args)
    unknown_args.pop('programs')
    print("Number of nested args to be parsed is",len(unknown_args))
    final_conf = m.get_nested_config(unknown_args)
    print("Args parsed from the nested config files: ", final_conf)
    print("Args from the parent cli program: ",args)




    