from typing import List, Tuple
from pydantic import BaseModel

class Create3dModelRequest(BaseModel):
    title: str
    story: str
    room_id: str
    index: int
