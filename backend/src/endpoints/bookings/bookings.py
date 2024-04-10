from fastapi import APIRouter
from src.endpoints.bookings.person_types import router as persons


router = APIRouter(prefix="/bookings", tags=["Bookings"])
router.include_router(persons)
