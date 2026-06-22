from functools import lru_cache

from app.features.forecasting.base import ForecastProvider


@lru_cache
def get_forecast_provider() -> ForecastProvider:
    from app.features.forecasting.xgboost_provider import XGBoostForecastProvider

    return XGBoostForecastProvider()