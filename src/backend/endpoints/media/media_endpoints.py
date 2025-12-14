from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/")
async def import_media(file_path: str):
    return FileResponse(file_path)
