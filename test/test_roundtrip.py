from opendp_logger import enable_logging, make_load_json
enable_logging()

from opendp.transformations import *
from opendp.measurements import *
from opendp.combinators import *
from opendp.typing import *
from opendp.mod import enable_features

enable_features("contrib")

def test_sized_mean():
    size = 1000
    bounds = (1.0, 10.0)
    meas = make_sized_bounded_mean(size, bounds) >> make_base_laplace(.01)
    serial = meas.to_json()
    make_load_json(serial)

def test_base_laplace():
    meas = make_base_laplace(.01)
    serial = meas.to_json()
    make_load_json(serial)

def test_base_gaussian():
    from opendp.measurements import make_base_gaussian
    from opendp.combinators import make_fix_delta, make_zCDP_to_approxDP
    delta = .000001
    meas = make_fix_delta(
        make_zCDP_to_approxDP(
            make_base_gaussian(scale=10.5, D="VectorDomain<AllDomain<f64>>")), delta)
    print("base gaussian:", meas([80., 90., 100.]))
    assert meas.check(1., (0.6, delta))
    make_load_json(meas.to_json())

def test_composition():
    composed = make_basic_composition([
        make_count(TIA=int, TO=int) >> make_basic_composition([
            make_base_discrete_laplace(scale=2.), 
            make_base_discrete_laplace(scale=200.)
        ]), 
        make_cast_default(int, bool) >> make_cast_default(bool, int) >> make_count(TIA=int, TO=int) >> make_base_discrete_laplace(scale=2.), 
        make_cast_default(int, float) >> make_clamp((0., 10.)) >> make_bounded_sum((0., 10.)) >> make_base_laplace(scale=2.), 

        make_basic_composition([
            make_count(TIA=int, TO=int) >> make_base_discrete_laplace(scale=2.), 
            make_count(TIA=int, TO=float) >> make_base_laplace(scale=2.),
            (
                make_cast_default(int, str) >> 
                make_count_by_categories(categories=["0", "12", "22"]) >> 
                make_base_discrete_laplace(scale=2., D=VectorDomain[AllDomain[int]])
            )
        ])
    ])

    make_load_json(composed.to_json())
