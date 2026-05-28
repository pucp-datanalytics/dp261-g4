from __future__ import annotations

from c_preprocessing import BOOLEAN_COLS, CATEGORICAL_COLS, NUMERIC_COLS, TARGET_COL


REQUIRED_INPUT_COLUMNS = NUMERIC_COLS + CATEGORICAL_COLS + BOOLEAN_COLS
OPTIONAL_TARGET_COLUMN = TARGET_COL
OPTIONAL_COLUMNS = [OPTIONAL_TARGET_COLUMN]
EXPECTED_UPLOAD_COLUMNS = REQUIRED_INPUT_COLUMNS + OPTIONAL_COLUMNS

EXPECTED_COLUMN_TYPES = {
    **{column: "numeric" for column in NUMERIC_COLS},
    **{column: "categorical" for column in CATEGORICAL_COLS},
    **{column: "boolean" for column in BOOLEAN_COLS},
    TARGET_COL: "boolean_target",
}

BOOLEAN_TRUE_VALUES = {"TRUE", "True", "true", "1", "SI", "Si", "si", "YES", "Yes", "yes", "Y", "y"}
BOOLEAN_FALSE_VALUES = {"FALSE", "False", "false", "0", "NO", "No", "no", "N", "n"}

KNOWN_MONTH_VALUES = {"Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}
KNOWN_VISITOR_TYPES = {"Returning_Visitor", "New_Visitor", "Other"}


def schema_as_dataframe_rows() -> list[dict]:
    rows = []
    for column in EXPECTED_UPLOAD_COLUMNS:
        rows.append(
            {
                "column": column,
                "required": column in REQUIRED_INPUT_COLUMNS,
                "type": EXPECTED_COLUMN_TYPES[column],
            }
        )
    return rows
