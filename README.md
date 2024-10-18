# OpenDP Logger
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)
[![ci tests](https://github.com/opendp/opendp-logger/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/opendp/opendp-logger/actions/workflows/smoke-test.yml?query=branch%3Amain)

The OpenDP logger makes it possible to serialize and deserialize OpenDP Measurements/Transformations to/from JSON.

## Usage

### Serialize
Enable logging (globally) before you build your transformations and/or measurements:

```python
from opendp_logging import enable_logging
enable_logging()
```
Once this is enabled, Transformations/Measurements have a method `.to_json()` that returns a JSON string.

### Deserialize
Deserialize a JSON string into a Transformation/Measurement by invoking `opendp_logger.make_load_json`.

### Example
```python
>>> from opendp_logger import enable_logging, make_load_json
>>> import opendp.prelude as dp

>>> enable_logging()
>>> dp.enable_features("contrib")

>>> preprocessor = (
...     # load data into a dataframe where columns are of type Vec<str>
...     dp.t.make_split_dataframe(separator=",", col_names=["hello", "world"])
...     >>
...     # select a column of the dataframe
...     dp.t.make_select_column(key="income", TOA=str)
... )

>>> # serialize the chain to json
>>> json_obj = preprocessor.to_json(indent=2)
>>> print(json_obj)
{
  "ast": {
    "_type": "constructor",
    "func": "make_chain_tt",
    "module": "combinators",
    "args": [
      {
        "_type": "constructor",
        "func": "make_select_column",
        "module": "transformations",
        "kwargs": {
          "key": "income",
          "TOA": "String"
        }
      },
      {
        "_type": "constructor",
        "func": "make_split_dataframe",
        "module": "transformations",
        "kwargs": {
          "separator": ",",
          "col_names": {
            "_type": "list",
            "_items": [
              "hello",
              "world"
            ]
          }
        }
      }
    ]
  }
}

>>> # reconstruct the obj from the json string
>>> make_load_json(json_obj)
Transformation(
    input_domain   = AtomDomain(T=String),
    output_domain  = VectorDomain(AtomDomain(T=String)),
    input_metric   = SymmetricDistance(),
    output_metric  = SymmetricDistance())

```

## Development

```shell
git clone https://github.com/opendp/opendp-logger.git
cd opendp-logger
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
pip install -e .
pytest -v
```