from fastapi import APIRouter

from api.images import router as files_router

router = APIRouter()

router.include_router(files_router)