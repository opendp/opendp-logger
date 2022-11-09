# OpenDP Logger
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)
[![ci tests](https://github.com/opendp/opendp-logger/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/opendp/opendp-logger/actions/workflows/smoke-test.yml?query=branch%3Amain)

The OpenDP logger makes it possible to serialize and deserialize OpenDP Measurements/Transformations to/from JSON.


## Serialize
Enable logging (globally) before you build your transformations and/or measurements:

```python
from opendp_logging import enable_logging
enable_logging()
```
Once this is enabled, Transformations/Measurements have a method `.to_json()` that returns a JSON string.

## Deserialize
Deserialize a JSON string into a Transformation/Measurement by invoking `opendp_logger.make_load_json`.

# Example
```python
from opendp_logger import enable_logging
from opendp.mod import enable_features

enable_logging()
enable_features("contrib")

import opendp.transformations as trans

preprocessor = (
    # load data into a dataframe where columns are of type Vec<str>
    trans.make_split_dataframe(separator=",", col_names=["hello", "world"])
    >>
    # select a column of the dataframe
    trans.make_select_column(key="income", TOA=str)
)

# serialize the chain to json
json_obj = preprocessor.to_json()
print("json:", json_obj)

from opendp_logger import make_load_json

# reconstruct the obj from the json string
test = make_load_json(json_obj)
```
