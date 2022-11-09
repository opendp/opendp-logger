import opendp

import json
import builtins

import pkg_resources

try:
    OPENDP_VERSION = pkg_resources.get_distribution("opendp").version
except pkg_resources.DistributionNotFound:
    OPENDP_VERSION = "0.0.0+development"

__all__ = ["make_load_json", "make_load_ast"]


def decode_ast(obj):
    if isinstance(obj, dict):
        if obj.get("_type") == "type":
            return getattr(builtins, obj["name"])

        if obj.get("_type") == "tuple":
            return tuple(decode_ast(i) for i in obj["_items"])

        if obj.get("_type") == "constructor":
            module = getattr(opendp, obj["module"])
            constructor = getattr(module, obj["func"])

            return constructor(*decode_ast(obj["args"]), **decode_ast(obj["kwargs"]))

        return {k: decode_ast(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [decode_ast(i) for i in obj]

    return obj


def make_load_json(parse_str: str):
    return make_load_ast(json.loads(parse_str))


def make_load_ast(obj):
    if obj["version"] != OPENDP_VERSION:
        raise ValueError(
            f"OpenDP version in parsed object ({obj['version']}) does not match the current installation ({OPENDP_VERSION})."
        )

    return decode_ast(obj["ast"])
