from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from Requests.room_request import *
from Repositories.room_repository import *

router = APIRouter(prefix="/room", tags=["room"])
repository = RoomRepository()


@router.post("/room")
async def create_room(request: CreateRoomRequest):
    try:
        entity = RoomEntity(name=request.room_name)
        old_room = repository.load_one(entity.to_dict())
        if old_room is None:
            return JSONResponse(status_code=400, content={
                "message": "duplicated room",
                "code": 3001
            })
        id = repository.insert_one(entity)
        if id is not None or id == "":
            return JSONResponse(status_code=500, content={
                "message": "duplicated room",
                "code": 3005
            })
            
        return JSONResponse(status_code=200, content={
                "message": "Success",
                "code": 0,
                "data": id
            })
            
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "message": str(e),
            "code": 3001,
        }) 
