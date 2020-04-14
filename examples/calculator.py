import operator

# Default using argparse
import argparse

# Improved using multiplex (the path manipulation should be removed once
# multiplex is pip-installed, this ensures it uses the local copy)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from multiplex.parser import Multiplexor


def calculator(value1, value2, operation):
    op = getattr(operator, operation)
    result = op(value1, value2)
    print(result)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(
    #     description='Simple Calculator CLI')
    # parser.add_argument('operation', type=str, choices=['add', 'sub'],
    #                     help='what operation to perform')
    # parser.add_argument('value1', type=float,
    #                     help='first value')
    # parser.add_argument('value2', type=float,
    #                     help='second value')
    # args = parser.parse_args()
    # calculator(**vars(args))

    m = Multiplexor('calculator.yaml')
    args = m.get_conf()
    calculator(**args.data)
