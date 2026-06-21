import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, engine
from app.features.auth.models import User
from app.features.datasets.models import Dataset
from app.features.profiling.models import DatasetProfile
from app.features.chat.models import ChatSession, ChatMessage

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
