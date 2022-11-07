from opendp_logger import enable_logging
from opendp.mod import enable_features

enable_logging()
enable_features("contrib")

import opendp.transformations as trans

preprocessor = (
    # Convert data into a dataframe where columns are of type Vec<str>
    trans.make_split_dataframe(separator=",", col_names=["hello", "world"])
    >>
    # Selects a column of df, Vec<str>
    trans.make_select_column(key="income", TOA=str)
)

# the ast object maintained in the pipeline
print("ast:", preprocessor.ast)

# the ast to json
json_obj = preprocessor.to_json()
print("json:", json_obj)

from opendp_logger import make_load_json

# reconstruct the obj from the json string
test = make_load_json(json_obj)

print(test.ast)
