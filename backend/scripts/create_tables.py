import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, engine
from app.features.auth.models import User  # noqa: F401
from app.features.datasets.models import Dataset  # noqa: F401
from app.features.profiling.models import DatasetProfile  # noqa: F401

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")