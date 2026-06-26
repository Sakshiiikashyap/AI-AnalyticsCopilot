from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth.models import User
from app.features.reports import service
from app.features.reports.schemas import ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{dataset_id}/generate", response_model=ReportResponse, status_code=201)
def generate_report(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.generate_report(db, str(current_user.id), dataset_id)


@router.get("/{report_id}/download")
def download_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = service.get_report(db, str(current_user.id), report_id)
    return FileResponse(
        path=run.file_path,
        media_type="application/pdf",
        filename="report-" + report_id + ".pdf",
    )