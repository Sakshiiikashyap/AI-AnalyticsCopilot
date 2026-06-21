from fastapi import APIRouter

from app.api.v1 import auth, chat, dashboard, datasets

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(datasets.router)
api_router.include_router(chat.router)
api_router.include_router(dashboard.router)
