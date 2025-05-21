from fastapi import APIRouter
from Requests.create_model_request import Create3dModelRequest
from Requests.response import BaseReponse
router = APIRouter(
    prefix="/model3d",
    tags=["model3d"]
)

@router.post("/create-3d-model")
async def create_3d_model(request: Create3dModelRequest):
    try:
        
        return JSONResponse(content={"result": "Ok"}, status_code=200);
    except Exception as e:
        return JSONResponse(content={"result": "failed"}, status_code=500);    