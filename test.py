# just an example script for WIP

from opendp.mod import enable_features
enable_features('contrib')
import opendp_logger.transformations as transformations
income_preprocessor = (
    # Convert data into a dataframe where columns are of type Vec<str>
    transformations.make_split_dataframe(separator=",", col_names=["hello", "world"]) >>
    # Selects a column of df, Vec<str>
    transformations.make_select_column(key="income", TOA=str)
)

# the ast object maintained in the pipeline
print("ast:", income_preprocessor.ast)

# the ast to json
json_obj = income_preprocessor.to_json()
print("json:", json_obj)

from opendp_logger.constructor import make_opendp_from_json

# reconstruct the obj from the json string
test = make_opendp_from_json(json_obj, ptype="json")

print(test.ast)
