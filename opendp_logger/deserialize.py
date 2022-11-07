import opendp.transformations as transformations
import opendp.measurements as measurements
import opendp.combinators as combinators

import json
import builtins

from opendp_logger.serialize import PT_TYPE_PREFIX, OPENDP_VERSION

__all__ = ["make_load_json", "make_load_object"]


def cast_str_to_type(d):
    for k, v in d.items():
        if isinstance(v, dict):
            cast_str_to_type(v)
        elif isinstance(v, str):
            if v.startswith(PT_TYPE_PREFIX):
                d[k] = getattr(builtins, v[len(PT_TYPE_PREFIX) :])
    return d


def jsonOpenDPDecoder(obj):
    if isinstance(obj, dict):
        return cast_str_to_type(obj)
    return obj


def cast_type_to_str(d):
    for k, v in d.items():
        if isinstance(v, dict):
            cast_type_to_str(v)
        elif isinstance(v, type):
            d[k] = "pytype_" + str(v.__name__)
    return d


def tree_walker(branch):
    if branch["module"] == "transformations":
        module = transformations
    elif branch["module"] == "measurements":
        module = measurements
    elif branch["module"] == "combinators":
        args = list(branch["args"])
        for i in range(len(branch["args"])):
            if isinstance(args[i], dict):
                args[i] = tree_walker(args[i])
        branch["args"] = tuple(args)

        for k, v in branch["kwargs"]:
            if isinstance(v, dict):
                branch["kwargs"][k] = tree_walker(v)

        module = combinators
    else:
        raise ValueError(
            f"Type {branch['type']} not in Literal[\"Transformation\", \"Measurement\"]."
        )

    return getattr(module, branch["func"])(*branch["args"], **branch["kwargs"])


def make_load_json(parse_str: str):
    obj = json.loads(parse_str, object_hook=jsonOpenDPDecoder)
    return make_load_object(obj)


def make_load_object(obj: str):
    if obj["version"] != OPENDP_VERSION:
        raise ValueError(
            f"OpenDP version in parsed object ({obj['version']}) does not match the current installation ({OPENDP_VERSION})."
        )

    return tree_walker(obj["ast"])
