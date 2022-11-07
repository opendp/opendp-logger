import opendp_logger.transformations as transformations
import opendp_logger.measurements as measurements
import opendp_logger.combinators as combinators

from typing import Literal
import json
import yaml
import builtins

from opendp_logger import OPENDP_VERSION
from opendp_logger.mods import PT_TYPE_PREFIX

def cast_str_to_type(d):
    for k, v in d.items():
        if isinstance(v, dict):
            cast_str_to_type(v)
        elif isinstance(v, str):
            if v.startswith(PT_TYPE_PREFIX):
                d[k] = getattr(builtins, v[len(PT_TYPE_PREFIX):])
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
            d[k] = "pytype_"+str(v.__name__)
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
        raise ValueError(f"Type {branch['type']} not in Literal[\"Transformation\", \"Measurement\"].")
    
    return getattr(module, branch["func"])(*branch["args"], **branch["kwargs"])

def make_opendp_from_json(parse_str: str, ptype: Literal["json", "yaml"]):
    if ptype == "json":
        obj = json.loads(parse_str, object_hook=jsonOpenDPDecoder)
    elif ptype == "yaml":
        obj = cast_str_to_type(yaml.load(parse_str))
    else:
        raise ValueError("Can only parse json and yaml formats.")

    if obj["version"] != OPENDP_VERSION:
        raise ValueError(
            f"OpenDP version in parsed object ({obj['version']}) does not match the current installation ({OPENDP_VERSION})."
            )
    
    return tree_walker(obj["ast"])
