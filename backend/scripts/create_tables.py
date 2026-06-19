"""Run once to create all tables in the database. Re-run anytime you add
a new model — it only creates tables that don't already exist."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, engine
from app.features.auth.models import User  # noqa: F401 — import so it registers with Base

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")