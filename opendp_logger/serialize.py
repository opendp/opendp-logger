from typing import get_type_hints
from opendp import Transformation, Measurement
import opendp as opendp
import json

import pkg_resources

import importlib


PT_TYPE_PREFIX = "py_type:"

# OPENDP version
try:
    OPENDP_VERSION = pkg_resources.get_distribution("opendp").version
except pkg_resources.DistributionNotFound:
    OPENDP_VERSION = "0.0.0+development"


# allow dumps to serialize object types
class DPL_Encoder(json.JSONEncoder):
    def default(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, type):
            return PT_TYPE_PREFIX + obj.__name__

        return obj.__dict__

    def encode(self, obj) -> str:
        def hint_tuples(item):
            if isinstance(item, tuple):
                return {"_tuple": True, "_items": [hint_tuples(e) for e in item]}
            if isinstance(item, list):
                return [hint_tuples(e) for e in item]
            if isinstance(item, dict):
                return {key: hint_tuples(value) for key, value in item.items()}
            else:
                return item

        return super().encode(hint_tuples(obj))


# export to json
def to_json(self):
    return json.dumps({"version": OPENDP_VERSION, "ast": self.ast}, cls=DPL_Encoder)


def wrapper(f_str, f, module_name):
    def wrapped(*args, **kwargs):
        ret_trans = f(*args, **kwargs)

        args = list(args)
        for i in range(len(args)):
            if type(args[i]) == Transformation or type(args[i]) == Measurement:
                # if an input hasn't been instrumented with an AST, return without an AST
                if not hasattr(args[i], "ast"):
                    return ret_trans

                args[i] = args[i].ast
        args = tuple(args)

        for k, v in kwargs.items():
            if type(v) == Transformation or type(v) == Measurement:
                # if an input hasn't been instrumented with an AST, return without an AST
                if not hasattr(v, "ast"):
                    return ret_trans

                kwargs[k] = v.ast

        ret_trans.ast = {
            "func": f_str,
            "module": module_name,
            "type": get_type_hints(f)["return"].__name__,
            "args": args,
            "kwargs": kwargs,
        }

        return ret_trans

    wrapped.__annotations__ = f.__annotations__
    wrapped.__doc__ = f.__doc__

    return wrapped


enabled = False


def enable_logging():

    global enabled
    if enabled:
        return

    for name in ["transformations", "measurements", "combinators"]:
        module = importlib.import_module(f"opendp.{name}")
        for f in dir(module):
            if f.startswith("make_"):
                module.__dict__[f] = wrapper(f, getattr(module, f), name)

    opendp.Transformation.to_json = to_json
    opendp.Measurement.to_json = to_json

    enabled = True
