import json
import opendp as opendp

from opendp_logger.constants import PT_TYPE_PREFIX, OPENDP_VERSION

import importlib

__all__ = ["enable_logging"]


def wrap_constructor(f_str, f, module_name):
    def wrapped(*args, **kwargs):
        chain = f(*args, **kwargs)
        chain.log = {
            "_type": "constructor",
            "func": f_str,
            "module": module_name,
            "args": args,
            "kwargs": kwargs,
        }
        return chain

    wrapped.__annotations__ = f.__annotations__
    wrapped.__doc__ = f.__doc__

    return wrapped


def to_ast(item):
    if isinstance(item, (opendp.Transformation, opendp.Measurement)):
        if not hasattr(item, "log"):
            msg = "invoke `opendp_logger.enable_logging()` before constructing your measurement"
            raise ValueError(msg)

        return to_ast(item.log)
    if isinstance(item, tuple):
        return {"_type": "tuple", "_items": [to_ast(e) for e in item]}
    if isinstance(item, list):
        return [to_ast(e) for e in item]
    if isinstance(item, dict):
        return {key: to_ast(value) for key, value in item.items()}
    if isinstance(item, type):
        return PT_TYPE_PREFIX + item.__name__
    if isinstance(item, opendp.typing.RuntimeType):
        return str(item)
    return item


def to_json(chain):
    return json.dumps({"version": OPENDP_VERSION, "ast": chain.to_ast()})


enabled = False


def enable_logging():

    global enabled
    if enabled:
        return

    for name in ["transformations", "measurements", "combinators"]:
        module = importlib.import_module(f"opendp.{name}")
        for f in dir(module):
            if f.startswith("make_"):
                module.__dict__[f] = wrap_constructor(f, getattr(module, f), name)

    opendp.Transformation.to_ast = to_ast
    opendp.Measurement.to_ast = to_ast

    opendp.Transformation.to_json = to_json
    opendp.Measurement.to_json = to_json

    enabled = True
