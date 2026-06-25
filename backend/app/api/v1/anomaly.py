from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.anomaly import service
from app.features.anomaly.schemas import AnomalyDetectionRequest, AnomalyResponse
from app.features.auth.models import User

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@router.post("/{dataset_id}", response_model=AnomalyResponse, status_code=201)
def create_anomaly_detection(
    dataset_id: str,
    payload: AnomalyDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = service.detect_anomalies(
        db, str(current_user.id), dataset_id, payload.method, payload.contamination
    )
    result = run.result_json
    return AnomalyResponse(
        dataset_id=run.dataset_id,
        method=run.method,
        columns_used=result["columns_used"],
        total_rows=result["total_rows"],
        anomaly_count=run.anomaly_count,
        anomalies=result["anomalies"],
    )