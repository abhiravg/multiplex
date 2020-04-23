# Inspired from https://github.com/pytorch/examples/blob/master/mnist/main.py

import os
import argparse

from multiplex import import_from_full_path, get_parser_from_module, get_entrypoint_from_module


def main():
    # There are four categories of arguments.
    #   1) args that should be parsed upstream, because they are
    #      common to both the main program and any subprograms. These
    #      are part of a shared_parser that will be inherited from by the
    #      subprogram's parser.
    #   2) args that should be parsed downstream, because only the
    #      subprogram needs them. These are specified by the subprogram's
    #      arguments parser.
    #   3) args that are upstream-only (should not be passed to subprograms).
    #      These should be only used if we do not call a subprogram.
    #   4) args that are downstream-only (should not be parsed by main program).
    #      These are quite rare, a good example being the help option.

    # First, create parser that will have shared arguments with subprograms (type 1)
    # Make sure, add_help is False, otherwise the subprogram will not receive the option -h.
    shared_parser = argparse.ArgumentParser(add_help=False)
    optional = shared_parser.add_argument_group('optional arguments')
    optional.add_argument('--no-cuda', action='store_true', default=False, help='disables CUDA training')
    optional.add_argument('--seed', type=int, default=1, metavar='S', help='random seed (default: 1)')

    # Then create another parser with all upstream-only args (type 3)
    # Add subprogram arg, limit choice of subprogram, but make it optional (nargs=?)
    programs = {'train': 'train.py', 'test': 'test.py'}
    exclusive_parser = argparse.ArgumentParser(add_help=False,)
    subprogram_group = exclusive_parser.add_argument_group('subprograms')
    subprogram_group.add_argument('program', nargs='?', choices=programs.keys())

    # The main program's parser is mostly complete now, with the exception of args of type 4.
    # We will only add these args of type 4 once we know we won't be running a subprogram.
    # To do this we will need to re-instantiate the parser, as any changes to the parent
    # parsers will not be registered by this parser[1].
    # [1](https://docs.python.org/3.8/library/argparse.html#parents)
    main_parser = argparse.ArgumentParser(description='PyTorch MNIST Example', add_help=False,
                                          parents=[exclusive_parser, shared_parser])

    # Parse only known arguments, capturing unknown ones for downstream processing
    args, unknown_args = main_parser.parse_known_args()

    # If a subprogram is selected, import it (by full path), run it's parser and pass the
    # restricted (without type 4 args) main parser as a parent parser, then
    # and call it's entry point (usually a main function that accepts a config object).
    # We can impose that the entry point only takes the conf as an argument, should we??
    if args.program:
        program_path = programs[args.program]
        program_path = os.path.abspath(program_path)
        subprogram = import_from_full_path(program_path)
        subparser = get_parser_from_module(subprogram, parents=[shared_parser])
        # Fix name of subparser
        subparser.prog = main_parser.prog + ' ' + args.program
        args = subparser.parse_args(args=unknown_args, namespace=args)
        main = get_entrypoint_from_module(subprogram)
        main(args)

    # Otherwise, re-parse all arguments of main program in order to generate
    # all the correct errors if unknown arguments are present[2].
    # At this point, we can also add any extra arguments (of type 4) that we
    # didn't want to capture earlier[3].
    #
    # Notes:
    # [2] We cannot just generate these errors ourselves from unknown_args like
    #     they do in argparse's source, because we may add options here. Because we
    #     are adding args, we need to 'refresh' the main parser.
    # [3] Should we special case these arguments?? Allow users to define which
    #     arguments should be captured by downstream programs instead of processed
    #     by the main one? Or, we could enforce strict-hierarchical argument capturing
    #     for everything except the help (which is usually automatically added if add_help).
    else:
        optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
        main_parser = argparse.ArgumentParser(description='PyTorch MNIST Example', add_help=False,
                                              parents=[exclusive_parser, shared_parser])
        args = main_parser.parse_args()
        print(args)  # TODO: call entry point main program, if any.


if __name__ == '__main__':
    main()
