from fastapi import APIRouter
from app.services.dashboard_services import get_dashboard_data

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def get_dashboard():
    return get_dashboard_data()