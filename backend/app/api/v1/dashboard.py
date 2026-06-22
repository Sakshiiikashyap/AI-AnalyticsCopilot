from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth.models import User
from app.features.chat.models import ChatSession
from app.features.datasets.models import Dataset
from app.features.forecasting.models import ForecastRun

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_datasets = db.query(func.count(Dataset.id)).filter(Dataset.user_id == current_user.id).scalar() or 0
    ready_datasets = (
        db.query(func.count(Dataset.id))
        .filter(Dataset.user_id == current_user.id, Dataset.status == "ready")
        .scalar()
        or 0
    )
    chat_sessions = (
        db.query(func.count(ChatSession.id)).filter(ChatSession.user_id == current_user.id).scalar() or 0
    )

    recent = (
        db.query(Dataset)
        .filter(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
        .limit(5)
        .all()
    )

    forecast_reports = (
        db.query(func.count(ForecastRun.id)).filter(ForecastRun.user_id == current_user.id).scalar() or 0
    )

    return {
        "total_datasets": total_datasets,
        "ready_datasets": ready_datasets,
        "chat_sessions": chat_sessions,
        "forecast_reports": forecast_reports,
        "recent_activity": [
            {
                "dataset_id": str(d.id),
                "name": d.name,
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in recent
        ],
    }