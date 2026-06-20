import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DatasetProfile(Base):
    __tablename__ = "dataset_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"))
    summary_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    missing_values_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    duplicates_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correlation_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    outliers_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())