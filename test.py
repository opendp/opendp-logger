# just an example script for WIP

from opendp.mod import enable_features
enable_features('contrib')
import opendp_logger.trans as trans
income_preprocessor = (
    # Convert data into a dataframe where columns are of type Vec<str>
    trans.make_split_dataframe(separator=",", col_names=["hello", "world"]) >>
    # Selects a column of df, Vec<str>
    trans.make_select_column(key="income", TOA=str)
)
income_preprocessor.ast

from opendp_logger.constructor import opendp_constructor
test = opendp_constructor(income_preprocessor.to_json(), ptype="json")

print(test.to_json())