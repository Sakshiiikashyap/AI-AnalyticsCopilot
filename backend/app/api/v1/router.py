from fastapi import APIRouter

from app.api.v1 import anomaly, auth, chat, dashboard, datasets, forecast, insights

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(datasets.router)
api_router.include_router(chat.router)
api_router.include_router(dashboard.router)
api_router.include_router(forecast.router)
api_router.include_router(anomaly.router)
api_router.include_router(insights.router)
