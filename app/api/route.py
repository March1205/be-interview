from fastapi import APIRouter

from app.api.routes import (
    organisations,
)

api_router = APIRouter()

api_router.include_router(
    organisations.router, prefix="/organisations", tags=["organisations"]
)
