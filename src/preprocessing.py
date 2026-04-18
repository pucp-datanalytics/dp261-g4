import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline


TARGET_COL = "Revenue"

NUM_COLS = [
    "Administrative",
    "Administrative_Duration",
    "Informational",
    "Informational_Duration",
    "ProductRelated",
    "ProductRelated_Duration",
    "BounceRates",
    "ExitRates",
    "PageValues",
    "SpecialDay",
]

CAT_COLS = [
    "Month",
    "OperatingSystems",
    "Browser",
    "Region",
    "TrafficType",
    "VisitorType",
]

BOOL_COLS = [
    "Weekend",
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates().copy()

    for col in CAT_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str)

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(int)

    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["total_paginas"] = (
        df["Administrative"] +
        df["Informational"] +
        df["ProductRelated"]
    )

    df["duracion_total"] = (
        df["Administrative_Duration"] +
        df["Informational_Duration"] +
        df["ProductRelated_Duration"]
    )

    return df


def get_model_columns():
    num_cols_model = NUM_COLS + ["total_paginas", "duracion_total"]
    cat_cols_model = CAT_COLS.copy()
    bool_cols_model = BOOL_COLS.copy()

    return num_cols_model, cat_cols_model, bool_cols_model


def build_preprocessor():
    num_cols_model, cat_cols_model, bool_cols_model = get_model_columns()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols_model),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols_model),
            ("bool", "passthrough", bool_cols_model),
        ]
    )

    return preprocessor


def build_pipeline(random_state: int = 42):
    preprocessor = build_preprocessor()

    pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=random_state)),
    ])

    return pipeline