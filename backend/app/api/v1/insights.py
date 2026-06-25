from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth.models import User
from app.features.insights import service
from app.features.insights.schemas import InsightResponse

router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("/{dataset_id}", response_model=InsightResponse, status_code=201)
def create_insights(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = service.generate_insights(db, str(current_user.id), dataset_id)
    result = run.result_json
    return InsightResponse(
        dataset_id=run.dataset_id,
        summary=result["summary"],
        key_findings=result["key_findings"],
        risks=result["risks"],
        opportunities=result["opportunities"],
        recommendations=result["recommendations"],
        generated_at=run.created_at,
    )