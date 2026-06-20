"""
File parsing + schema inference.

Built defensively for real-world messy data, not just clean test files:
- handles inconsistent column name whitespace
- detects dates even when stored as text in mixed formats
- treats common missing-value placeholders as actual nulls
- doesn't crash on empty files or unsupported types — raises clean errors instead
"""
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.shared.exceptions import ValidationFailedError

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

# Common real-world placeholder strings that mean "missing", beyond pandas' defaults
EXTRA_NA_VALUES = ["NA", "N/A", "n/a", "null", "NULL", "-", "--", "?", "none", "None", "#N/A"]


def load_dataframe(file_path: str) -> pd.DataFrame:
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValidationFailedError(f"Unsupported file type: {ext}")

    try:
        if ext == ".csv":
            df = pd.read_csv(file_path, low_memory=False, na_values=EXTRA_NA_VALUES, keep_default_na=True)
        else:
            df = pd.read_excel(file_path, na_values=EXTRA_NA_VALUES, keep_default_na=True)
    except Exception as exc:
        raise ValidationFailedError(f"Could not parse file: {exc}") from exc

    if df.empty:
        raise ValidationFailedError("Uploaded file contains no rows.")

    # Normalize column names: strip whitespace, since real-world headers often
    # have leading/trailing spaces (" Revenue " vs "Revenue")
    df.columns = [str(c).strip() for c in df.columns]

    # Drop fully-empty columns that sometimes appear from trailing commas in CSVs
    df = df.dropna(axis=1, how="all")

    return df


def _infer_semantic_type(series: pd.Series) -> str:
    """Goes beyond raw pandas dtype to a business-friendly category."""
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "integer" if pd.api.types.is_integer_dtype(series) else "float"

    if series.dtype == object:
        sample = series.dropna().head(20)
        if len(sample) > 0:
            try:
                parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
                if parsed.notna().mean() > 0.8:
                    return "datetime"
            except Exception:
                pass

        nunique = series.nunique(dropna=True)
        if nunique <= max(20, int(len(series) * 0.05)):
            return "categorical"
        return "text"

    return "unknown"


def infer_schema(df: pd.DataFrame) -> dict[str, Any]:
    columns_info = []
    for col in df.columns:
        series = df[col]
        semantic_type = _infer_semantic_type(series)
        col_info: dict[str, Any] = {
            "name": col,
            "dtype": str(series.dtype),
            "semantic_type": semantic_type,
            "null_count": int(series.isna().sum()),
            "unique_count": int(series.nunique(dropna=True)),
        }
        if semantic_type in ("integer", "float"):
            desc = series.describe()
            col_info["min"] = _safe_float(desc.get("min"))
            col_info["max"] = _safe_float(desc.get("max"))
            col_info["mean"] = _safe_float(desc.get("mean"))
        columns_info.append(col_info)

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": columns_info,
    }


def _safe_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return None
    return float(value)


def dataframe_preview(df: pd.DataFrame, limit: int = 50) -> dict[str, Any]:
    preview_df = df.head(limit).replace({np.nan: None})
    return {
        "columns": list(df.columns),
        "rows": preview_df.to_dict(orient="records"),
        "total_rows": int(len(df)),
    }