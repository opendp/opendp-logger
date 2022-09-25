from typing import Literal, get_type_hints, Union
from opendp import Transformation, Measurement
import opendp as opendp
import json
import yaml

import pkg_resources

# OPENDP version
OPENDP_VERSION = pkg_resources.get_distribution("opendp").version

# allow dumps to serialize object types
def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, type):
        serial = "py_type:"+obj.__name__
        return serial

    return obj.__dict__

# export to json
def to_json(self):
    return json.dumps(
        {
            "version": OPENDP_VERSION,
            "ast": self.ast
        },
        default=serialize
    )

"""# export to yaml
def to_yaml(self):
    return yaml.dump(
        {
            "version": OPENDP_VERSION,
            "ast": cast_type_to_str(self.ast)
        }
    )"""


def wrapper(f_str, f, module_name):
    def wrapped(*args, **kwargs):
        ret_trans = f(*args, **kwargs)

        args = list(args)
        for i in range(len(args)):
            if type(args[i]) == Transformation or  type(args[i]) == Measurement:
                args[i] = args[i].ast
        args = tuple(args)

        for k, v in kwargs.items():
            if type(v) == Transformation or  type(v) == Measurement:
                kwargs[k] = v.ast

        ret_trans.ast = {
            "func": f_str,
            "module": module_name,
            "type": get_type_hints(f)['return'].__name__,
            "args": args,
            "kwargs": kwargs
        }

        return ret_trans

    return wrapped

def Measurement__rshift__(self, other: "Transformation"):
    if isinstance(other, Transformation):
        from opendp_logger.comb import make_chain_tm
        return make_chain_tm(other, self)

    raise ValueError(f"rshift expected a postprocessing transformation, got {other}")

def Transformation__rshift__(self, other: Union["Measurement", "Transformation"]):
    if isinstance(other, Measurement):
        from opendp_logger.comb import make_chain_mt
        return make_chain_mt(other, self)

    if isinstance(other, Transformation):
        from opendp_logger.comb import make_chain_tt
        return make_chain_tt(other, self)

    raise ValueError(f"rshift expected a measurement or transformation, got {other}")

Transformation = opendp.Transformation
Measurement = opendp.Measurement

Transformation.ast = None
#copy_rshift = Transformation.__rshift__
Transformation.__rshift__ = Transformation__rshift__
Measurement.__rshift__ = Measurement__rshift__

Transformation.to_json = to_json
#Transformation.to_yaml = to_yaml
Measurement.to_json = to_json
#Measurement.to_yaml = to_yaml