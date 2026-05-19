from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42
TARGET_COL = "Revenue"
RAW_SOURCE = Path("docs/dataset_pucp.csv")
RAW_COPY = Path("data/raw/c_dataset_pucp.csv")

NUMERIC_COLS = [
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

CATEGORICAL_COLS = [
    "Month",
    "OperatingSystems",
    "Browser",
    "Region",
    "TrafficType",
    "VisitorType",
]

BOOLEAN_COLS = ["Weekend"]
ENGINEERED_COLS = [
    "c_total_pages",
    "c_total_duration",
    "c_product_share",
    "c_page_value_per_product",
]
EXPECTED_COLS = NUMERIC_COLS + CATEGORICAL_COLS + BOOLEAN_COLS + [TARGET_COL]


def ensure_dirs() -> None:
    for path in [
        "data/raw",
        "data/interim",
        "data/processed",
        "models",
        "reports",
        "dashboard",
        "handoff/contracts",
        "handoff/model",
    ]:
        Path(path).mkdir(parents=True, exist_ok=True)


def copy_raw_dataset() -> None:
    ensure_dirs()
    if not RAW_SOURCE.exists():
        raise FileNotFoundError(f"No se encontro el dataset oficial: {RAW_SOURCE}")
    RAW_COPY.write_bytes(RAW_SOURCE.read_bytes())


def normalize_target(y: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(y) or pd.api.types.is_numeric_dtype(y):
        return y.astype(int)
    return y.astype(str).str.upper().map({"TRUE": 1, "FALSE": 0, "1": 1, "0": 0}).astype(int)


def load_raw_data(path: str | Path = RAW_SOURCE) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in EXPECTED_COLS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esperadas: {missing}")
    return df[EXPECTED_COLS].copy()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates().copy()
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in CATEGORICAL_COLS:
        df[col] = df[col].astype("string")
    for col in BOOLEAN_COLS:
        if pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(int)
        else:
            df[col] = df[col].astype(str).str.upper().map({"TRUE": 1, "FALSE": 0, "1": 1, "0": 0}).astype(int)
    df[TARGET_COL] = normalize_target(df[TARGET_COL])
    return df


def add_features(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    total_pages = X["Administrative"] + X["Informational"] + X["ProductRelated"]
    total_duration = (
        X["Administrative_Duration"]
        + X["Informational_Duration"]
        + X["ProductRelated_Duration"]
    )
    X["c_total_pages"] = total_pages
    X["c_total_duration"] = total_duration
    X["c_product_share"] = X["ProductRelated"] / total_pages.replace(0, 1)
    X["c_page_value_per_product"] = X["PageValues"] / X["ProductRelated"].replace(0, 1)
    return X


def feature_groups() -> tuple[list[str], list[str], list[str]]:
    return NUMERIC_COLS + ENGINEERED_COLS, CATEGORICAL_COLS, BOOLEAN_COLS


def build_preprocessor() -> ColumnTransformer:
    num_cols, cat_cols, bool_cols = feature_groups()
    num_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    bool_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent"))])
    return ColumnTransformer(
        [
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols),
            ("bool", bool_pipe, bool_cols),
        ],
        verbose_feature_names_out=True,
    )


def build_model_pipeline(classifier, use_smote: bool = True) -> ImbPipeline:
    steps = [("preprocessor", build_preprocessor())]
    if use_smote:
        steps.append(("smote", SMOTE(random_state=RANDOM_STATE)))
    steps.append(("classifier", classifier))
    return ImbPipeline(steps)


def load_and_split(test_size: float = 0.2):
    copy_raw_dataset()
    df = clean_data(load_raw_data())
    df.to_csv("data/interim/c_clean_dataset.csv", index=False)
    X = add_features(df.drop(columns=[TARGET_COL]))
    y = df[TARGET_COL]
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=RANDOM_STATE)


def prepare_data():
    X_train, X_test, y_train, y_test = load_and_split()
    train = X_train.copy()
    train[TARGET_COL] = y_train.to_numpy()
    test = X_test.copy()
    test[TARGET_COL] = y_test.to_numpy()
    train.to_csv("data/processed/c_train.csv", index=False)
    test.to_csv("data/processed/c_test.csv", index=False)
    pd.concat([train, test], ignore_index=True).to_csv("data/processed/c_processed_dataset.csv", index=False)

    preproc = build_preprocessor()
    preproc.fit(X_train)
    joblib.dump(preproc, "models/c_preproc.pkl")
    joblib.dump(preproc, "models/c_preprocessing_pipeline.pkl")

    X_train_t = preproc.transform(X_train)
    X_bal, y_bal = SMOTE(random_state=RANDOM_STATE).fit_resample(X_train_t, y_train)
    balanced = pd.DataFrame(X_bal, columns=preproc.get_feature_names_out())
    balanced[TARGET_COL] = y_bal.to_numpy()
    balanced.to_csv("data/processed/c_train_balanced.csv", index=False)
    return X_train, X_test, y_train, y_test
