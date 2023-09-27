from opendp_logger import enable_logging, make_load_json
enable_logging()

import pytest
import sys
import opendp.prelude as dp

@pytest.mark.skipif('polars' not in sys.modules,
                    reason="requires the Polars library")
def test_with_counts():
    import polars as pl
    domains, data = [
        dp.series_domain("A", dp.atom_domain(T=float)),
        dp.series_domain("B", dp.atom_domain(T=int)),
        dp.series_domain("C", dp.option_domain(dp.atom_domain(T=str))),
    ], {
        "A": [1.0] * 50,
        "B": [1] * 50,
        "C": ["1"] * 50,
    }
    domain, data = dp.lazyframe_domain(domains), pl.LazyFrame(data, schema_overrides={"B": pl.Int32})
    domain = domain.with_counts(pl.LazyFrame({"B": [1], "counts": [50]}, schema_overrides={"B": pl.Int32, "counts": pl.UInt32}))

    assert make_load_json(domain.to_json()) == domain
