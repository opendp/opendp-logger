import opendp.prelude as dp
import importlib

import json
import builtins

__all__ = ["make_load_json", "make_load_ast"]


def decode_ast(obj):
    if isinstance(obj, dict):
        if obj.get("_type") == "type":
            return getattr(builtins, dp.RuntimeType.parse(obj["name"]))  # pragma: no cover

        if obj.get("_type") == "list":
            return [decode_ast(i) for i in obj["_items"]]

        if obj.get("_type") == "constructor":
            module = importlib.import_module(f"opendp.{obj['module']}")
            constructor = getattr(module, obj["func"])

            return constructor(*decode_ast(obj.get("args", ())), **decode_ast(obj.get("kwargs", {})))
        
        if obj.get("_type") == "partial_chain":
            return decode_ast(obj["lhs"]) >> decode_ast(obj["rhs"])
    
        return {k: decode_ast(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return tuple(decode_ast(i) for i in obj)

    return obj


def make_load_json(parse_str: str):
    return make_load_ast(json.loads(parse_str))


def make_load_ast(obj, force=False):
    # TODO: Reenable when we can get the OpenDP version:
    # https://github.com/opendp/opendp/issues/2103
    #
    # if obj["version"] != OPENDP_VERSION and not force:
    #     raise ValueError(
    #         f"OpenDP version in parsed object ({obj['version']}) does not match the current installation ({OPENDP_VERSION}). Set `force=True` to try to load anyways."
    #     )

    return decode_ast(obj["ast"])
