from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/image360", tags=["image360"])


@router.post("/create-image-360")
async def create_image_360():
    try:
        return JSONResponse(status_code=200, content="application/json")
    except Exception as e:
        return HTTPException(status_code=500)
