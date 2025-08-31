from fastapi import APIRouter

from tutorioal_fastapi_chank.src.api.images import router as files_router

router = APIRouter()

router.include_router(files_router)