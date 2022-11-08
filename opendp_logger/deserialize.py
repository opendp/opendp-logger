import opendp.transformations as transformations
import opendp.measurements as measurements
import opendp.combinators as combinators

import json
import builtins

from opendp_logger.serialize import PT_TYPE_PREFIX, OPENDP_VERSION

__all__ = ["make_load_json", "make_load_object"]


def jsonOpenDPDecoder(obj):
    if isinstance(obj, dict):
        if obj.get("_type") == "Tuple":
            return tuple(jsonOpenDPDecoder(i) for i in obj["_items"])
        return {k: jsonOpenDPDecoder(v) for k, v in obj.items()}

    if isinstance(obj, str) and obj.startswith(PT_TYPE_PREFIX):
        return getattr(builtins, obj[len(PT_TYPE_PREFIX) :])
    return obj


def tree_walker(branch):
    if isinstance(branch, dict):
        if branch.get('_type') == "constructor":
            branch = {
                **branch,
                "args": tuple(tree_walker(i) for i in branch['args']),
                "kwargs": {k: tree_walker(v) for k, v in branch['kwargs'].items()},
            }
            if branch["module"] == "transformations":
                module = transformations
            elif branch["module"] == "measurements":
                module = measurements
            elif branch["module"] == "combinators":
                module = combinators
            else:
                raise ValueError(
                    f"Type {branch['type']} not in Literal[\"Transformation\", \"Measurement\"]."
                )
            return getattr(module, branch["func"])(*branch["args"], **branch["kwargs"])
        return {k: tree_walker(v) for k, v in branch.items()}
    
    if isinstance(branch, list):
        return list(tree_walker(i) for i in branch)
    
    return branch


def make_load_json(parse_str: str):
    obj = json.loads(parse_str, object_hook=jsonOpenDPDecoder)
    return make_load_object(obj)


def make_load_object(obj: str):
    if obj["version"] != OPENDP_VERSION:
        raise ValueError(
            f"OpenDP version in parsed object ({obj['version']}) does not match the current installation ({OPENDP_VERSION})."
        )

    return tree_walker(obj["ast"])
