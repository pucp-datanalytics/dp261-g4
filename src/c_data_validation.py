from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pandas as pd

from c_input_schema import (
    BOOLEAN_FALSE_VALUES,
    BOOLEAN_TRUE_VALUES,
    KNOWN_MONTH_VALUES,
    KNOWN_VISITOR_TYPES,
    OPTIONAL_TARGET_COLUMN,
    REQUIRED_INPUT_COLUMNS,
)
from c_preprocessing import BOOLEAN_COLS, CATEGORICAL_COLS, NUMERIC_COLS, TARGET_COL, add_features


@dataclass
class DatasetValidationResult:
    is_valid: bool
    raw_df: pd.DataFrame
    validated_df: pd.DataFrame
    model_input: pd.DataFrame
    target: pd.Series | None
    missing_columns: list[str]
    extra_columns: list[str]
    null_counts: dict[str, int]
    warnings: list[str]
    has_target: bool


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]
    return normalized


def read_uploaded_dataset(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(BytesIO(file_bytes))
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(BytesIO(file_bytes))
    raise ValueError("Formato no soportado. Usa CSV o XLSX.")


def parse_boolean_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(int)
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce").map({1: 1, 0: 0})
    normalized = series.astype(str).str.strip()
    return normalized.map(lambda value: 1 if value in BOOLEAN_TRUE_VALUES else 0 if value in BOOLEAN_FALSE_VALUES else pd.NA)


def validate_dataset(raw_df: pd.DataFrame) -> DatasetValidationResult:
    warnings: list[str] = []
    if raw_df.empty:
        return DatasetValidationResult(
            is_valid=False,
            raw_df=raw_df,
            validated_df=pd.DataFrame(),
            model_input=pd.DataFrame(),
            target=None,
            missing_columns=REQUIRED_INPUT_COLUMNS.copy(),
            extra_columns=[],
            null_counts={},
            warnings=["El archivo cargado esta vacio."],
            has_target=False,
        )

    df = normalize_column_names(raw_df)
    missing_columns = [column for column in REQUIRED_INPUT_COLUMNS if column not in df.columns]
    extra_columns = [column for column in df.columns if column not in REQUIRED_INPUT_COLUMNS + [OPTIONAL_TARGET_COLUMN]]
    has_target = TARGET_COL in df.columns
    if missing_columns:
        return DatasetValidationResult(
            is_valid=False,
            raw_df=df,
            validated_df=pd.DataFrame(),
            model_input=pd.DataFrame(),
            target=None,
            missing_columns=missing_columns,
            extra_columns=extra_columns,
            null_counts=df.isna().sum().to_dict(),
            warnings=warnings,
            has_target=has_target,
        )

    validated = df[REQUIRED_INPUT_COLUMNS + ([TARGET_COL] if has_target else [])].copy()
    for column in NUMERIC_COLS:
        before_nulls = int(validated[column].isna().sum())
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
        after_nulls = int(validated[column].isna().sum())
        if after_nulls > before_nulls:
            warnings.append(f"La columna {column} contiene valores no numericos; se marcaron como nulos para imputacion del pipeline.")

    for column in CATEGORICAL_COLS:
        validated[column] = validated[column].astype("string").str.strip()
        if validated[column].isna().any():
            warnings.append(f"La columna {column} contiene nulos; el pipeline imputara el valor mas frecuente.")

    for column in BOOLEAN_COLS:
        parsed = parse_boolean_series(validated[column])
        invalid_count = int(parsed.isna().sum())
        if invalid_count:
            warnings.append(f"La columna {column} tiene {invalid_count} valores booleanos no reconocidos.")
        validated[column] = parsed.astype("Int64")

    target = None
    if has_target:
        parsed_target = parse_boolean_series(validated[TARGET_COL])
        invalid_target = int(parsed_target.isna().sum())
        if invalid_target:
            warnings.append(f"La columna {TARGET_COL} tiene {invalid_target} valores no reconocidos; esas filas no sirven para metricas reales.")
        validated[TARGET_COL] = parsed_target.astype("Int64")
        target = validated[TARGET_COL].dropna().astype(int)

    unknown_months = set(validated["Month"].dropna().astype(str).unique()) - KNOWN_MONTH_VALUES
    if unknown_months:
        warnings.append(f"Month contiene categorias no vistas o poco usuales: {sorted(unknown_months)}.")
    unknown_visitors = set(validated["VisitorType"].dropna().astype(str).unique()) - KNOWN_VISITOR_TYPES
    if unknown_visitors:
        warnings.append(f"VisitorType contiene categorias no vistas o poco usuales: {sorted(unknown_visitors)}.")

    null_counts = validated.isna().sum().astype(int).to_dict()
    model_base = validated.drop(columns=[TARGET_COL], errors="ignore")
    model_input = add_features(model_base)
    return DatasetValidationResult(
        is_valid=True,
        raw_df=df,
        validated_df=validated,
        model_input=model_input,
        target=target,
        missing_columns=[],
        extra_columns=extra_columns,
        null_counts=null_counts,
        warnings=warnings,
        has_target=has_target,
    )


def write_uploaded_outputs(validated_df: pd.DataFrame, predictions: pd.DataFrame | None = None) -> None:
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    validated_df.to_csv("data/processed/c_uploaded_dataset_validated.csv", index=False)
    if predictions is not None and not predictions.empty:
        predictions.to_csv("data/processed/c_uploaded_predictions.csv", index=False)


def validation_summary(result: DatasetValidationResult) -> dict:
    return {
        "is_valid": result.is_valid,
        "rows": int(len(result.raw_df)),
        "columns": int(result.raw_df.shape[1]) if not result.raw_df.empty else 0,
        "has_target": result.has_target,
        "missing_columns": result.missing_columns,
        "extra_columns": result.extra_columns,
        "total_nulls": int(sum(result.null_counts.values())) if result.null_counts else 0,
        "warnings": result.warnings,
    }
