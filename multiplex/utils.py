import functools
import os
from importlib import util

PARSER_GETTERS = {}
ENTRY_POINTS = {}


def register_parser(fn):
    """Decorator used to register a module's get_parser

    Simply register the function in `PARSER_GETTERS` and return the function intact.

    Args:
        fn: The decorated function. It must return a argparse.ArgumentParser object,
            and at a minimum, take in a list of parent parsers.

    Returns:
        The original function (not changed in any way).
    """
    if fn.__module__ in PARSER_GETTERS:
        raise ValueError("Cannot register multiple parsers per submodule.")
    PARSER_GETTERS[fn.__module__] = fn

    @functools.wraps(fn)
    def registered(*args, **kwargs):
        return fn(*args, **kwargs)

    return registered


def get_parser_from_module(subprogram, *args, parents=None, **kwargs):
    """Retrieves the corresponding parser of the subprogram.
    This only works if the subprogram has a properly decorated
    function that will return a parser. See: @register_parser

    Args:
        subprogram: The subprogram module
        *args:      Arbitrary arguments
        parents:    List of parent parsers
        **kwargs:   Arbitrary keyword arguments

    Returns:
        The subprogram's parser.
    """
    subparser = PARSER_GETTERS.get(subprogram.__name__)
    if subparser is None:
        raise ValueError(f"No subparser found for module {subprogram.__name__}, "
                         f"consider using the @register_parser decorator.")
    parents = [] if parents is None else parents
    return subparser(*args, parents=parents, **kwargs)


def register_entrypoint(fn):
    if fn.__module__ in ENTRY_POINTS:
        raise ValueError("Cannot register multiple entry points per submodule.")
    ENTRY_POINTS[fn.__module__] = fn

    @functools.wraps(fn)
    def registered(*args, **kwargs):
        return fn(*args, **kwargs)

    return registered


def get_entrypoint_from_module(subprogram):
    name = "__main__" if subprogram is None else subprogram.__name__
    main = ENTRY_POINTS.get(name)
    if main is None:
        raise ValueError(f"No entry point found for module {name}, "
                         f"consider using the @register_entrypoint decorator.")
    return main


def import_from_full_path(full_path, module_name=None, submodules_path=None):
    if module_name is None:
        module_name, _ = os.path.splitext(os.path.basename(full_path))
    if submodules_path is None:
        submodules_path = os.path.dirname(full_path)
    spec = util.spec_from_file_location(module_name, full_path,
                                        submodule_search_locations=submodules_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def to_nested_dict(d, dotlist_sep='.'):
    new = {}

    def add_element(key, value):
        if dotlist_sep in key:
            subdict = new
            for part in key.split(dotlist_sep)[:-1]:
                if part not in subdict:
                    subdict[part] = {}
                subdict = subdict[part]
            subdict[key.split(dotlist_sep)[-1]] = value
        else:
            new[key] = value

    for key, value in d.items():
        add_element(key, value)
    return new
