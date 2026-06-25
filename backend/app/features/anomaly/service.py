"""
Anomaly detection service.

Isolation Forest: an unsupervised ML algorithm that isolates anomalies by
randomly partitioning the feature space. Points that get isolated in fewer
partitioning steps (i.e. are "easy to separate" from the rest of the data)
are scored as more anomalous. Works well for multivariate anomalies - rows
that look fine column-by-column but are unusual in combination.

DBSCAN: a density-based clustering algorithm. Points that don't belong to
any dense cluster (density below eps/min_samples thresholds) are labeled
as noise - which we treat as anomalies. Better suited for data with natural
cluster structure; more sensitive to parameter tuning than Isolation Forest.
"""
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.features.anomaly.models import AnomalyRun
from app.features.datasets.models import Dataset
from app.features.datasets.service import get_dataframe_for_dataset, get_dataset
from app.shared.exceptions import ValidationFailedError, parse_uuid


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def _prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    numeric_cols = _numeric_columns(df)
    if len(numeric_cols) < 2:
        raise ValidationFailedError("Anomaly detection requires at least 2 numeric columns.")

    feature_df = df[numeric_cols].copy()
    feature_df = feature_df.fillna(feature_df.median(numeric_only=True))
    return feature_df, numeric_cols


def _run_isolation_forest(feature_df: pd.DataFrame, contamination: float) -> np.ndarray:
    """Returns anomaly scores where LOWER (more negative) = more anomalous,
    normalized to 0-1 where 1 = most anomalous, for consistent UI display."""
    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    model.fit(feature_df)
    raw_scores = model.score_samples(feature_df)
    predictions = model.predict(feature_df)

    normalized = (raw_scores.max() - raw_scores) / (raw_scores.max() - raw_scores.min() + 1e-9)
    is_anomaly = predictions == -1
    return normalized, is_anomaly


def _run_dbscan(feature_df: pd.DataFrame, contamination: float) -> tuple[np.ndarray, np.ndarray]:
    """DBSCAN labels noise points as -1. We use a heuristic eps based on
    feature scale since DBSCAN has no contamination parameter directly."""
    scaled = StandardScaler().fit_transform(feature_df)
    model = DBSCAN(eps=1.5, min_samples=max(5, int(len(feature_df) * 0.02)))
    labels = model.fit_predict(scaled)

    is_anomaly = labels == -1
    distances = np.zeros(len(feature_df))
    if is_anomaly.any() and (~is_anomaly).any():
        from sklearn.metrics import pairwise_distances

        cluster_points = scaled[~is_anomaly]
        for i in range(len(scaled)):
            if is_anomaly[i]:
                dists = pairwise_distances([scaled[i]], cluster_points)
                distances[i] = dists.min()
    max_dist = distances.max() if distances.max() > 0 else 1.0
    normalized_scores = distances / max_dist
    return normalized_scores, is_anomaly


def detect_anomalies(
    db: Session, user_id: str, dataset_id: str, method: str, contamination: float
) -> AnomalyRun:
    dataset: Dataset = get_dataset(db, user_id, dataset_id)
    df = get_dataframe_for_dataset(dataset)

    if len(df) < 20:
        raise ValidationFailedError("Anomaly detection requires at least 20 rows of data.")

    feature_df, numeric_cols = _prepare_features(df)

    if method == "dbscan":
        scores, is_anomaly = _run_dbscan(feature_df, contamination)
    else:
        method = "isolation_forest"
        scores, is_anomaly = _run_isolation_forest(feature_df, contamination)

    anomaly_indices = np.where(is_anomaly)[0]
    anomalies = []
    for idx in anomaly_indices:
        row_data = df.iloc[int(idx)].replace({np.nan: None}).to_dict()
        anomalies.append(
            {
                "row_index": int(idx),
                "anomaly_score": round(float(scores[idx]), 4),
                "row_data": {k: (v if not isinstance(v, (np.integer, np.floating)) else float(v)) for k, v in row_data.items()},
            }
        )
    anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)

    result = {
        "columns_used": numeric_cols,
        "total_rows": int(len(df)),
        "anomalies": anomalies,
    }

    run = AnomalyRun(
        dataset_id=parse_uuid(dataset_id, "dataset"),
        user_id=parse_uuid(user_id, "user"),
        method=method,
        anomaly_count=len(anomalies),
        result_json=result,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run