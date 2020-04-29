import operator

# Improved using multiplex
from multiplex import Multiplexor


# Default using argparse
# import argparse


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
