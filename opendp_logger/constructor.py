import opendp_logger.trans as trans
import opendp_logger.meas as meas

from typing import Literal
import json
import yaml
import re
import builtins

PT_TYPE = "^py_type:*"

from opendp_logger import OPENDP_VERSION

blocklist = {
    "Measurement": [],
    "Transformation": []
}

def cast_str_to_type(d):
    for k, v in d.items():
        if isinstance(v, dict):
            cast_str_to_type(v)
        elif isinstance(v, str):
            if re.search(PT_TYPE, v):
                d[k] = getattr(builtins, v[8:])
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
    if isinstance(branch, dict):
        keys = branch.keys()
        if ('to' in keys) and ('from' in keys):
            return tree_walker(branch["from"]) >> tree_walker(branch["to"])
    if branch["type"] == "Transformation":
        return getattr(trans, branch["func"])(*branch["args"], **branch["kwargs"])
    elif branch["type"] == "Measurement":
        return getattr(meas, branch["func"])(*branch["args"], **branch["kwargs"])
    else:
        raise ValueError(f"Type {branch['type']} not in Literal[\"Transformation\", \"Measurement\"].")

def opendp_constructor(parse_str: str, ptype: Literal["json", "yaml"]):
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
