import opendp.transformations as transformations
import opendp.measurements as measurements
import opendp.combinators as combinators

import json
import builtins
from opendp_logger.constants import PT_TYPE_PREFIX, OPENDP_VERSION

__all__ = ["make_load_json", "make_load_ast"]


def decode_ast(obj):
    if isinstance(obj, dict):
        if obj.get("_type") == "tuple":
            return tuple(decode_ast(i) for i in obj["_items"])

        if obj.get("_type") == "constructor":
            obj = {
                **obj,
                "args": decode_ast(obj["args"]),
                "kwargs": decode_ast(obj["kwargs"]),
            }
            if obj["module"] == "transformations":
                module = transformations
            elif obj["module"] == "measurements":
                module = measurements
            elif obj["module"] == "combinators":
                module = combinators
            else:
                raise ValueError(f"Unrecognized module {obj['module']}.")

            return getattr(module, obj["func"])(*obj["args"], **obj["kwargs"])

        else:
            return {k: decode_ast(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return list(decode_ast(i) for i in obj)

    if isinstance(obj, str) and obj.startswith(PT_TYPE_PREFIX):
        return getattr(builtins, obj[len(PT_TYPE_PREFIX) :])

    return obj


def make_load_json(parse_str: str):
    return make_load_ast(json.loads(parse_str))


def make_load_ast(obj):
    if obj["version"] != OPENDP_VERSION:
        raise ValueError(
            f"OpenDP version in parsed object ({obj['version']}) does not match the current installation ({OPENDP_VERSION})."
        )

    return decode_ast(obj["ast"])
