"""
Dataset service — upload handling, persistence, retrieval, deletion.

File storage: saved to a per-user folder on disk (UPLOAD_DIR). For real
production scale this swaps to S3-compatible object storage behind this
same interface without touching callers.
"""
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.features.datasets import parser
from app.features.datasets.models import Dataset
from app.shared.exceptions import NotFoundError, ValidationFailedError, parse_uuid

ALLOWED_CONTENT_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def _user_upload_dir(user_id: str) -> Path:
    path = Path(settings.UPLOAD_DIR) / user_id
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload(user_id: str, file: UploadFile) -> tuple[str, str]:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_CONTENT_EXTENSIONS:
        raise ValidationFailedError("Only .csv and .xlsx files are supported.")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise ValidationFailedError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.")

    safe_name = f"{uuid.uuid4()}{ext}"
    dest_path = _user_upload_dir(user_id) / safe_name
    dest_path.write_bytes(contents)

    file_type = "csv" if ext == ".csv" else "xlsx"
    return str(dest_path), file_type


def create_dataset(db: Session, user_id: str, original_filename: str, file_path: str, file_type: str) -> Dataset:
    dataset = Dataset(
        user_id=parse_uuid(user_id, "user"),
        name=Path(original_filename).stem,
        original_filename=original_filename,
        file_path=file_path,
        file_type=file_type,
        status="processing",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def process_dataset(db: Session, dataset: Dataset) -> Dataset:
    """Parses the file and stores schema info. Synchronous for now — fine at
    this scale; moves to a background task/queue once files get large."""
    try:
        df = parser.load_dataframe(dataset.file_path)
        schema = parser.infer_schema(df)

        dataset.row_count = schema["row_count"]
        dataset.column_count = schema["column_count"]
        dataset.schema_json = schema
        dataset.status = "ready"
        db.commit()
    except Exception:
        dataset.status = "failed"
        db.commit()
        raise
    db.refresh(dataset)
    return dataset


def list_datasets(db: Session, user_id: str) -> list[Dataset]:
    return (
        db.query(Dataset)
        .filter(Dataset.user_id == parse_uuid(user_id, "user"))
        .order_by(Dataset.created_at.desc())
        .all()
    )


def get_dataset(db: Session, user_id: str, dataset_id: str) -> Dataset:
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == parse_uuid(dataset_id, "dataset"), Dataset.user_id == parse_uuid(user_id, "user"))
        .first()
    )
    if not dataset:
        raise NotFoundError("Dataset not found.")
    return dataset


def delete_dataset(db: Session, user_id: str, dataset_id: str) -> None:
    dataset = get_dataset(db, user_id, dataset_id)
    file_path = Path(dataset.file_path)
    if file_path.exists():
        file_path.unlink()
    db.delete(dataset)
    db.commit()


def get_dataframe_for_dataset(dataset: Dataset):
    return parser.load_dataframe(dataset.file_path)