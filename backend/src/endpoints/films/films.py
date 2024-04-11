from fastapi import APIRouter
from src.endpoints.films.halls import router as halls


router = APIRouter(prefix="/films", tags=["Films"])
router.include_router(halls)
