"""
Automated data profiling engine.

Computes, in pure pandas/numpy (no LLM involved - this is the ground
truth the AI chat feature will be grounded against later):
  - per-column summary statistics
  - missing values analysis
  - duplicate row detection
  - correlation matrix for numeric columns
  - outlier detection using the IQR method (fast, explainable; a
    dedicated Isolation Forest / DBSCAN anomaly detector is a separate
    feature later, for multivariate anomaly detection)
"""
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.features.datasets.models import Dataset
from app.features.profiling.models import DatasetProfile


def _safe(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return None
    return float(value)


def _column_summary(df: pd.DataFrame) -> dict[str, Any]:
    summaries = []
    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        entry: dict[str, Any] = {
            "name": col,
            "dtype": str(series.dtype),
            "count": int(series.notna().sum()),
            "null_count": null_count,
            "null_percentage": round(null_count / len(df) * 100, 2) if len(df) else 0.0,
            "unique_count": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe()
            entry.update(
                {
                    "mean": _safe(desc.get("mean")),
                    "std": _safe(desc.get("std")),
                    "min": _safe(desc.get("min")),
                    "median": _safe(desc.get("50%")),
                    "max": _safe(desc.get("max")),
                }
            )
        else:
            top = series.value_counts(dropna=True).head(5)
            entry["top_values"] = [{"value": str(k), "count": int(v)} for k, v in top.items()]
        summaries.append(entry)

    return {"row_count": int(len(df)), "column_count": int(len(df.columns)), "columns": summaries}


def _missing_values(df: pd.DataFrame) -> dict[str, Any]:
    null_counts = df.isna().sum()
    total = len(df)
    per_column = [
        {
            "column": col,
            "missing_count": int(null_counts[col]),
            "missing_percentage": round(float(null_counts[col]) / total * 100, 2) if total else 0.0,
        }
        for col in df.columns
        if null_counts[col] > 0
    ]
    per_column.sort(key=lambda x: x["missing_percentage"], reverse=True)
    return {
        "total_missing_cells": int(null_counts.sum()),
        "columns_with_missing": per_column,
        "complete_rows": int(len(df.dropna())),
    }


def _correlation(df: pd.DataFrame) -> dict[str, Any]:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return {"available": False, "reason": "Fewer than 2 numeric columns.", "matrix": {}, "strong_pairs": []}

    corr = numeric_df.corr(numeric_only=True).round(3)
    matrix = corr.replace({np.nan: None}).to_dict()

    strong_pairs = []
    cols = corr.columns.tolist()
    for i, col_a in enumerate(cols):
        for col_b in cols[i + 1:]:
            value = corr.loc[col_a, col_b]
            if pd.notna(value) and abs(value) >= 0.6:
                strong_pairs.append({"column_a": col_a, "column_b": col_b, "correlation": float(value)})
    strong_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    return {"available": True, "matrix": matrix, "strong_pairs": strong_pairs}


def _outliers_iqr(df: pd.DataFrame) -> dict[str, Any]:
    numeric_df = df.select_dtypes(include=[np.number])
    results = []
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if len(series) < 4:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outlier_mask = (series < lower) | (series > upper)
        count = int(outlier_mask.sum())
        if count > 0:
            results.append(
                {
                    "column": col,
                    "outlier_count": count,
                    "outlier_percentage": round(count / len(series) * 100, 2),
                    "lower_bound": _safe(lower),
                    "upper_bound": _safe(upper),
                }
            )
    results.sort(key=lambda x: x["outlier_count"], reverse=True)
    return {"method": "IQR (1.5x)", "columns": results}


def compute_profile(df: pd.DataFrame) -> dict[str, Any]:
    """Pure function: DataFrame in, profile dict out. Easy to test in isolation."""
    return {
        "summary": _column_summary(df),
        "missing_values": _missing_values(df),
        "duplicates_count": int(df.duplicated().sum()),
        "correlation": _correlation(df),
        "outliers": _outliers_iqr(df),
    }


def generate_profile(db: Session, dataset: Dataset, df: pd.DataFrame) -> DatasetProfile:
    """Computes the profile and upserts it for the given dataset."""
    result = compute_profile(df)

    existing = db.query(DatasetProfile).filter(DatasetProfile.dataset_id == dataset.id).first()
    profile = existing if existing else DatasetProfile(dataset_id=dataset.id)
    if not existing:
        db.add(profile)

    profile.summary_json = result["summary"]
    profile.missing_values_json = result["missing_values"]
    profile.duplicates_count = result["duplicates_count"]
    profile.correlation_json = result["correlation"]
    profile.outliers_json = result["outliers"]

    db.commit()
    db.refresh(profile)
    return profile