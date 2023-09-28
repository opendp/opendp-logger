import opendp.prelude as dp
import json
from functools import wraps

from opendp_logger.deserialize import OPENDP_VERSION, LazyFrame, DataFrame

import importlib

__all__ = ["enable_logging"]
LOGGED_CLASSES = (
    dp.Transformation,
    dp.Measurement,
    dp.Function,
    dp.Domain,
    dp.Metric,
    dp.Measure,
    dp.PartialConstructor,
)
WRAPPED_MODULES = [
    "transformations",
    "measurements",
    "combinators",
    "domains",
    "metrics",
    "measures",
    "prelude",
    "core",
]


def wrap_func(f, module_name):
    @wraps(f)
    def wrapper(*args, **kwargs):
        chain = f(*args, **kwargs)
        if isinstance(chain, LOGGED_CLASSES):
            chain.log = {
                "_type": "constructor",
                "func": f.__name__,
                "module": module_name,
            }
            args and chain.log.setdefault("args", args)
            kwargs and chain.log.setdefault("kwargs", kwargs)
        return chain

    return wrapper


def to_ast(item):
    if isinstance(item, LOGGED_CLASSES):
        if not hasattr(item, "log"):
            msg = "invoke `opendp_logger.enable_logging()` before constructing your measurement"
            print(item)
            raise ValueError(msg)

        return to_ast(item.log)
    if isinstance(item, tuple):
        return [to_ast(e) for e in item]
    if isinstance(item, DataFrame):
        # TODO: extremely inefficient
        return {"_type": "DataFrame", "_item": item.lazy().serialize()}
    if isinstance(item, LazyFrame):
        return {"_type": "LazyFrame", "_item": item.serialize()}
    if isinstance(item, list):
        return {"_type": "list", "_items": [to_ast(e) for e in item]}
    if isinstance(item, dict):
        return {key: to_ast(value) for key, value in item.items()}
    if isinstance(item, (dp.RuntimeType, type)):
        return str(dp.RuntimeType.parse(item))
    return item


def to_json(chain, *args, **kwargs):
    return json.dumps(
        {"version": OPENDP_VERSION, "ast": chain.to_ast()}, *args, **kwargs
    )

WHITELIST = [
    "lazyframe_domain_with_counts",
    "dataframe_domain_with_counts",
    "l1",
    "l2",
    "transformation_function"
]

def enable_logging():
    for name in WRAPPED_MODULES:
        module = importlib.import_module(f"opendp.{name}")
        for f in dir(module):
            is_constructor = f.startswith("make_") or f.startswith("then_")
            is_elem = any(f.endswith(s) for s in ["domain", "distance", "divergence"])
            if is_constructor or is_elem or f in WHITELIST:
                module.__dict__[f] = wrap_func(getattr(module, f), name)

    for cls in LOGGED_CLASSES:
        cls.to_ast = to_ast
        cls.to_json = to_json

    trans_shift_inner = dp.Transformation.__rshift__

    @wraps(trans_shift_inner)
    def trans_shift_outer(lhs: dp.Transformation, rhs):
        chain = trans_shift_inner(lhs, rhs)
        if isinstance(rhs, dp.PartialConstructor):
            chain.log = {"_type": "partial_chain", "lhs": lhs.log, "rhs": rhs.log}
        return chain

    dp.Transformation.__rshift__ = trans_shift_outer

    meas_shift_inner = dp.Measurement.__rshift__

    @wraps(meas_shift_inner)
    def meas_shift_outer(lhs: dp.Measurement, rhs):
        chain = meas_shift_inner(lhs, rhs)
        if isinstance(rhs, dp.PartialConstructor):
            chain.log = {"_type": "partial_chain", "lhs": lhs.log, "rhs": rhs.log}
        return chain

    dp.Measurement.__rshift__ = meas_shift_outer

    # only run once
    enable_logging.__code__ = (lambda: None).__code__
