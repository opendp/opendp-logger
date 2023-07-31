from opendp_logger import enable_logging, make_load_json

enable_logging()

import opendp.prelude as dp

dp.enable_features("contrib")


def test_sized_mean():
    size = 1000
    bounds = (1.0, 10.0)
    space = dp.vector_domain(dp.atom_domain(bounds), size), dp.symmetric_distance()
    meas = space >> dp.t.then_mean() >> dp.m.then_laplace(0.01)
    serial = meas.to_json()
    make_load_json(serial)


def test_base_laplace():
    space = dp.atom_domain(T=float), dp.absolute_distance(T=float)
    meas = space >> dp.m.then_laplace(0.01)
    serial = meas.to_json()
    make_load_json(serial)


def test_base_gaussian():
    delta = 0.000001
    space = dp.vector_domain(dp.atom_domain(T=float)), dp.l2_distance(T=float)
    meas = dp.c.make_fix_delta(
        dp.c.make_zCDP_to_approxDP(space >> dp.m.then_gaussian(scale=10.5)), delta
    )
    print("base gaussian:", meas([80.0, 90.0, 100.0]))
    assert meas.check(1.0, (0.6, delta))
    make_load_json(meas.to_json())


def test_composition():
    space = dp.vector_domain(dp.atom_domain(T=int)), dp.symmetric_distance()
    int_space = dp.atom_domain(T=int), dp.absolute_distance(T=int)
    composed = dp.c.make_basic_composition(
        [
            space
            >> dp.t.then_count(TO=int)
            >> dp.c.make_basic_composition(
                [
                    int_space >> dp.m.then_laplace(scale=2.0),
                    int_space >> dp.m.then_laplace(scale=200.0),
                ]
            ),
            space
            >> dp.t.then_cast_default(bool)
            >> dp.t.then_cast_default(int)
            >> dp.t.then_count(TO=int)
            >> dp.m.then_laplace(scale=2.0),
            space
            >> dp.t.then_cast_default(float)
            >> dp.t.then_clamp((0.0, 10.0))
            >> dp.t.then_sum()
            >> dp.m.then_laplace(scale=2.0),
            dp.c.make_basic_composition(
                [
                    space >> dp.t.then_count(TO=int) >> dp.m.then_laplace(scale=2.0),
                    space >> dp.t.then_count(TO=float) >> dp.m.then_laplace(scale=2.0),
                    (
                        space
                        >> dp.t.then_cast_default(str)
                        >> dp.t.then_count_by_categories(categories=["0", "12", "22"])
                        >> dp.m.then_laplace(scale=2.0)
                    ),
                ]
            ),
        ]
    )

    make_load_json(composed.to_json())
