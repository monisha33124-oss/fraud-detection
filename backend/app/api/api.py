from fastapi import APIRouter
from app.api.endpoints import auth, transactions, alerts, investigations, reports, customers, analytics, audit, models

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["investigations"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
