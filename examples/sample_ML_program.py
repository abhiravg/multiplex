import operator

# Default using argparse
import argparse

# Improved using multiplex (the path manipulation should be removed once
# multiplex is pip-installed, this ensures it uses the local copy)
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiplex.parser import Multiplexor

if __name__ == "__main__":
    
    m = Multiplexor('sample_ML_config.yaml')
    args = m.get_conf()
    print(args.data.get('programs'))
    print(args.data.get('seed'))
    m.run_command(args)