import pandas as pd
from sqlalchemy.orm import Session

from app.features.datasets.models import Dataset
from app.features.datasets.service import get_dataframe_for_dataset, get_dataset
from app.features.forecasting.factory import get_forecast_provider
from app.features.forecasting.models import ForecastRun
from app.shared.exceptions import ValidationFailedError, parse_uuid


def _auto_detect_date_column(df: pd.DataFrame):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if df[col].dtype == object:
            parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
            if parsed.notna().mean() > 0.8:
                return col
    return None


def _auto_detect_metric_column(df: pd.DataFrame, exclude: str):
    numeric_cols = [c for c in df.select_dtypes(include="number").columns if c != exclude]
    if not numeric_cols:
        return None
    priority = ["revenue", "sales", "amount", "price", "value", "quantity", "temp"]
    for keyword in priority:
        for col in numeric_cols:
            if keyword in col.lower():
                return col
    return numeric_cols[0]


def run_forecast(db: Session, user_id: str, dataset_id: str, date_column, metric_column, periods: int) -> ForecastRun:
    dataset: Dataset = get_dataset(db, user_id, dataset_id)
    df = get_dataframe_for_dataset(dataset)

    if date_column is None:
        date_column = _auto_detect_date_column(df)
    if not date_column or date_column not in df.columns:
        raise ValidationFailedError("Could not find a usable date column. Forecasting requires a date/time column.")

    if metric_column is None:
        metric_column = _auto_detect_metric_column(df, exclude=date_column)
    if not metric_column or metric_column not in df.columns:
        raise ValidationFailedError("Could not find a usable numeric column to forecast.")

    working = df[[date_column, metric_column]].copy()
    working[date_column] = pd.to_datetime(working[date_column], errors="coerce", format="mixed")
    working = working.dropna(subset=[date_column, metric_column])
    working = working.groupby(date_column, as_index=False)[metric_column].sum().sort_values(date_column)

    if len(working) < 15:
        raise ValidationFailedError("Not enough historical data points to forecast (need at least 15 dated rows).")

    provider = get_forecast_provider()
    try:
        result = provider.forecast(
            dates=working[date_column].tolist(), values=working[metric_column].tolist(), periods=periods
        )
    except ValueError as e:
        raise ValidationFailedError(str(e))

    run = ForecastRun(
        dataset_id=parse_uuid(dataset_id, "dataset"),
        user_id=parse_uuid(user_id, "user"),
        date_column=date_column,
        metric_column=metric_column,
        periods=periods,
        result_json=result,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run