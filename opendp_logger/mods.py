from opendp import Transformation, Measurement
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


def wrapper(f_str, f):
    def wrapped(*args, **kwargs):
        ret_trans = f(*args, **kwargs)

        ret_trans.ast = {
            "func": f_str,
            "type": ("Transformation" if type(ret_trans) == Transformation else "Measurement"),
            "args": args,
            "kwargs": kwargs
        }

        return ret_trans

    return wrapped

def new_rshift(self, other):
  ret = copy_rshift(self, other)
  ret.ast = {"from": self.ast, "to":other.ast}
  return ret

Transformation.ast = None
copy_rshift = Transformation.__rshift__
Transformation.__rshift__ = new_rshift

Transformation.to_json = to_json
#Transformation.to_yaml = to_yaml
Measurement.to_json = to_json
#Measurement.to_yaml = to_yaml