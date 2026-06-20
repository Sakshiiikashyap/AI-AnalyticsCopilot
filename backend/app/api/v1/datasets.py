from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.features.auth.models import User
from app.features.datasets import service
from app.features.datasets.parser import dataframe_preview
from app.features.datasets.schemas import DatasetPreviewResponse, DatasetResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetResponse, status_code=201)
async def upload_dataset(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path, file_type = await service.save_upload(str(current_user.id), file)
    dataset = service.create_dataset(db, str(current_user.id), file.filename or "dataset", file_path, file_type)
    dataset = service.process_dataset(db, dataset)
    return dataset


@router.get("", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.list_datasets(db, str(current_user.id))


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_dataset(db, str(current_user.id), dataset_id)


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service.delete_dataset(db, str(current_user.id), dataset_id)
    return None


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = service.get_dataset(db, str(current_user.id), dataset_id)
    df = service.get_dataframe_for_dataset(dataset)
    return dataframe_preview(df)