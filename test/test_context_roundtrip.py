from opendp_logger import enable_logging, make_load_json
from random import randint
import pytest

enable_logging()

import opendp.prelude as dp

dp.enable_features("contrib")


def test_context():
    privacy_unit = dp.unit_of(contributions=1)
    privacy_loss = dp.loss_of(epsilon=1.)
    bounds = (0.0, 100.0)
    imputed_value = 50.0
    data = [float(randint(0, 100)) for _ in range(100)]
    context = dp.Context.compositor(
        data=data,
        privacy_unit=privacy_unit,
        privacy_loss=privacy_loss,
        split_evenly_over=3
    )
    count_query = (
        context.query()
        .count()
        .laplace()
    )
    serialized_query = count_query.resolve().to_json()

    # TODO:
    #     def trans_shift_outer(lhs: dp.Transformation, rhs):
    #         chain = trans_shift_inner(lhs, rhs)
    #         if isinstance(rhs, dp.PartialConstructor):
    # >           chain.log = {"_type": "partial_chain", "lhs": lhs.log, "rhs": rhs.log}
    # E           AttributeError: 'PartialConstructor' object has no attribute 'log'

    count_query_again = make_load_json(serialized_query)
    assert count_query_again.param() == ...
    assert count_query_again.release() == ...

