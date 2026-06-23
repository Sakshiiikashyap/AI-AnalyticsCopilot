from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth.models import User
from app.features.forecasting import service
from app.features.forecasting.schemas import ForecastRequest, ForecastResponse

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.post("/{dataset_id}", response_model=ForecastResponse, status_code=201)
def create_forecast(
    dataset_id: str,
    payload: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = service.run_forecast(
        db, str(current_user.id), dataset_id, payload.date_column, payload.metric_column, payload.periods
    )
    result = run.result_json
    return ForecastResponse(
        dataset_id=run.dataset_id,
        date_column=run.date_column,
        metric_column=run.metric_column,
        method=result["method"],
        frequency=result["frequency"],
        history=result["history"],
        forecast=result["forecast"],
        backtest=result.get("backtest"),
    )