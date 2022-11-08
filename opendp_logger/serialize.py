from typing import get_type_hints
from opendp import Transformation, Measurement
import opendp as opendp
from opendp.typing import RuntimeType
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
        if isinstance(obj, RuntimeType):
            return str(obj)

        return obj.__dict__

    def encode(self, obj) -> str:
        def walker(item):
            if isinstance(item, (Transformation, Measurement)):
                return walker(item.ast)
            if isinstance(item, tuple):
                return {"_type": "Tuple", "_items": [walker(e) for e in item]}
            if isinstance(item, list):
                return [walker(e) for e in item]
            if isinstance(item, dict):
                return {key: walker(value) for key, value in item.items()}
            else:
                return item
    
        return super().encode(walker(obj))


# export to json
def to_json(self):
    return json.dumps({"version": OPENDP_VERSION, "ast": self.ast}, cls=DPL_Encoder)


def wrapper(f_str, f, module_name):
    def wrapped(*args, **kwargs):
        chain = f(*args, **kwargs)
        chain.ast = {
            "_type": "constructor",
            "func": f_str,
            "module": module_name,
            "type": get_type_hints(f)["return"].__name__,
            "args": args,
            "kwargs": kwargs,
        }
        return chain

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
