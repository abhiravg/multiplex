import operator

# Default using argparse
import argparse

# Improved using multiplex (the path manipulation should be removed once
# multiplex is pip-installed, this ensures it uses the local copy)
import os
import sys
from multiplex import import_from_full_path, get_parser_from_module, get_entrypoint_from_module
from multiplex import Multiplexor

if __name__ == "__main__":
    
    m = Multiplexor('sample_ML_config.yaml')
    args, subprogram_args = m.get_conf()
    if args.data.get('programs'):
        program_path = args.data.get('programs')
        program_path = os.path.abspath(program_path)
        subprogram = import_from_full_path(program_path)
        #subparser = get_parser_from_module(subprogram, parents=[shared_parser])
        # Fix name of subparser
        #subparser.prog = main_parser.prog + ' ' + args.program
        #args = subparser.parse_args(args=unknown_args, namespace=args)
        main = get_entrypoint_from_module(subprogram)
        main(args, subprogram_args)