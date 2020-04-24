import os
import functools
import importlib

PARSER_GETTERS = {}
SUBPROGRAM_ENTRY_POINTS = {}


def register_parser(fn):
    if fn.__module__ in PARSER_GETTERS:
        raise ValueError("Cannot register multiple parsers per submodule.")
    PARSER_GETTERS[fn.__module__] = fn

    @functools.wraps(fn)
    def registered(*args, **kwargs):
        return fn(*args, **kwargs)
    return registered


def get_parser_from_module(subprogram, *args, **kwargs):
    # Should we allow the get parser to take in arguments??
    # What's a use case for that?
    subparser = PARSER_GETTERS.get(subprogram.__name__)
    if subparser is None:
        raise ValueError(f"No subparser found for module {subprogram.__name__}, "
                         f"consider using the @register_parser decorator.")
    return subparser(*args, **kwargs)


def register_entrypoint(fn):
    if fn.__module__ in SUBPROGRAM_ENTRY_POINTS:
        raise ValueError("Cannot register multiple entry points per submodule.")
    SUBPROGRAM_ENTRY_POINTS[fn.__module__] = fn

    @functools.wraps(fn)
    def registered(*args, **kwargs):
        return fn(*args, **kwargs)
    return registered


def get_entrypoint_from_module(subprogram):
    main = SUBPROGRAM_ENTRY_POINTS.get(subprogram.__name__)
    if main is None:
        raise ValueError(f"No entry point found for module {subprogram.__name__}, "
                         f"consider using the @register_entrypoint decorator.")
    return main


def import_from_full_path(full_path, module_name=None, submodules_path=None):
    if module_name is None:
        module_name, _ = os.path.splitext(os.path.basename(full_path))
    if submodules_path is None:
        submodules_path = os.path.dirname(full_path)
    spec = importlib.util.spec_from_file_location(module_name, full_path,
                                                  submodule_search_locations=submodules_path)
    module = importlib.util.module_from_spec(spec)
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
