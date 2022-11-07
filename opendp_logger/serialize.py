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
def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, type):
        return PT_TYPE_PREFIX + obj.__name__

    return obj.__dict__


# export to json
def to_json(self):
    return json.dumps({"version": OPENDP_VERSION, "ast": self.ast}, default=serialize)


# # export to yaml
# def to_yaml(self):
#     return yaml.dump({"version": OPENDP_VERSION, "ast": cast_type_to_str(self.ast)})


def wrapper(f_str, f, module_name):
    def wrapped(*args, **kwargs):
        ret_trans = f(*args, **kwargs)

        args = list(args)
        for i in range(len(args)):
            if type(args[i]) == Transformation or type(args[i]) == Measurement:
                args[i] = args[i].ast
        args = tuple(args)

        for k, v in kwargs.items():
            if type(v) == Transformation or type(v) == Measurement:
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
    # opendp.Transformation.to_yaml = to_yaml
    # opendp.Measurement.to_yaml = to_yaml

    enabled = True
