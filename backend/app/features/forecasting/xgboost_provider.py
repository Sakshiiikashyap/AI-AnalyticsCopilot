"""
XGBoost-based time series forecaster, with backtest accuracy validation.

Approach:
  1. Hold out the most recent N real data points as a test set.
  2. Train on everything before that, forecast forward to "predict" the
     held-out period, and compare against what actually happened (MAE, RMSE).
     This gives an honest accuracy estimate, not just a black-box forecast.
  3. Re-train on the FULL dataset and forecast forward into the real future
     for the actual output.
  4. Confidence intervals are approximated from training residual std dev,
     since XGBoost has no native predictive uncertainty.
"""
from typing import Any

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from app.features.forecasting.base import ForecastProvider

LAGS = [1, 2, 3, 7]
ROLLING_WINDOWS = [3, 7]
MIN_TRAINING_ROWS = 15


class XGBoostForecastProvider(ForecastProvider):
    def forecast(self, dates: list, values: list, periods: int) -> dict[str, Any]:
        df = pd.DataFrame({"date": pd.to_datetime(dates), "value": values}).sort_values("date").reset_index(drop=True)

        if len(df) < MIN_TRAINING_ROWS:
            raise ValueError("Not enough historical data points to forecast (need at least 15).")

        freq = _infer_frequency(df["date"])

        backtest_metrics = self._run_backtest(df, periods, freq)

        forecast_points, history_points = self._fit_and_forecast(df, periods, freq)

        warning = None
        if periods > len(df) * 0.5:
            warning = (
                "This forecast extends quite far relative to the amount of historical data available "
                "(" + str(periods) + " periods requested vs " + str(len(df)) + " historical points). "
                "Treat longer-horizon predictions with extra caution."
            )

        return {
            "method": "XGBoost (lag and calendar features, recursive multi-step)",
            "frequency": freq,
            "history": history_points,
            "forecast": forecast_points,
            "backtest": backtest_metrics,
            "warning": warning,
        }

    def _run_backtest(self, df: pd.DataFrame, periods: int, freq: str) -> dict[str, Any] | None:
        """Holds out the most recent points, retrains without them, predicts
        them, and compares to what actually happened. Returns None if there
        isn't enough data left over to do this meaningfully."""
        holdout_size = min(periods, max(5, int(len(df) * 0.15)))
        if len(df) - holdout_size < MIN_TRAINING_ROWS:
            return None

        train_part = df.iloc[: len(df) - holdout_size].reset_index(drop=True)
        actual_part = df.iloc[len(df) - holdout_size :].reset_index(drop=True)

        try:
            predicted_points, _ = self._fit_and_forecast(train_part, holdout_size, freq)
        except ValueError as e:
            return None

        predicted_values = np.array([p["value"] for p in predicted_points])
        actual_values = actual_part["value"].to_numpy()

        mae = float(np.mean(np.abs(predicted_values - actual_values)))
        rmse = float(np.sqrt(np.mean((predicted_values - actual_values) ** 2)))
        mean_actual = float(np.mean(actual_values))
        mae_pct = round(mae / mean_actual * 100, 2) if mean_actual != 0 else None

        return {
            "holdout_periods": holdout_size,
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "mae_percentage_of_mean": mae_pct,
        }

    def _fit_and_forecast(self, df: pd.DataFrame, periods: int, freq: str) -> tuple[list, list]:
        """Core fit + recursive forecast logic, reused for both backtesting
        and the real future forecast. Returns (forecast_points, history_points)."""
        features_df = _build_features(df)
        train_df = features_df.dropna()
        if len(train_df) < 10:
            raise ValueError("Not enough data after feature engineering to train a forecast model.")

        feature_cols = [c for c in train_df.columns if c not in ("date", "value")]
        X_train = train_df[feature_cols]
        y_train = train_df["value"]

        model = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
        model.fit(X_train, y_train)

        residuals = y_train - model.predict(X_train)
        residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.0

        history = df.copy()
        forecast_points = []

        for step in range(1, periods + 1):
            next_date = _next_date(history["date"].iloc[-1], freq)
            row_features = _build_single_feature_row(history, feature_cols, next_date)
            pred = float(model.predict(pd.DataFrame([row_features]))[0])

            margin = 1.96 * residual_std * (1 + step * 0.1)
            forecast_points.append(
                {
                    "date": str(next_date.date()),
                    "value": round(pred, 4),
                    "lower_bound": round(pred - margin, 4),
                    "upper_bound": round(pred + margin, 4),
                }
            )
            history = pd.concat([history, pd.DataFrame([{"date": next_date, "value": pred}])], ignore_index=True)

        history_points = [{"date": str(d.date()), "value": float(v)} for d, v in zip(df["date"], df["value"])]
        return forecast_points, history_points


def _infer_frequency(dates: pd.Series) -> str:
    diffs = dates.sort_values().diff().dropna().dt.days
    if diffs.empty:
        return "D"
    median_days = diffs.median()
    if median_days <= 1:
        return "D"
    if median_days <= 7:
        return "W"
    return "ME"


def _next_date(last_date: pd.Timestamp, freq: str) -> pd.Timestamp:
    if freq == "D":
        return last_date + pd.Timedelta(days=1)
    if freq == "W":
        return last_date + pd.Timedelta(weeks=1)
    return last_date + pd.DateOffset(months=1)


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for lag in LAGS:
        out["lag_" + str(lag)] = out["value"].shift(lag)
    for window in ROLLING_WINDOWS:
        out["rolling_mean_" + str(window)] = out["value"].shift(1).rolling(window).mean()
    out["day_of_week"] = out["date"].dt.dayofweek
    out["day_of_month"] = out["date"].dt.day
    out["month"] = out["date"].dt.month
    return out


def _build_single_feature_row(history: pd.DataFrame, feature_cols: list, next_date: pd.Timestamp) -> dict:
    row: dict[str, Any] = {}
    values = history["value"].values
    for lag in LAGS:
        col = "lag_" + str(lag)
        if col in feature_cols:
            row[col] = float(values[-lag]) if len(values) >= lag else float(values[-1])
    for window in ROLLING_WINDOWS:
        col = "rolling_mean_" + str(window)
        if col in feature_cols:
            row[col] = float(np.mean(values[-window:])) if len(values) >= window else float(np.mean(values))
    if "day_of_week" in feature_cols:
        row["day_of_week"] = next_date.dayofweek
    if "day_of_month" in feature_cols:
        row["day_of_month"] = next_date.day
    if "month" in feature_cols:
        row["month"] = next_date.month
    return row