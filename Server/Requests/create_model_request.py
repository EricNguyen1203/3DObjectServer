from typing import List, Tuple
from pydantic import BaseModel

class Create3dModelRequest(BaseModel):
    title: str
    story: str
    room_id: str
    index: int


class Character(BaseModel):
    name: str
    position: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    rotation: Tuple[float, float, float]


class Update3dModelRequest(BaseModel):
    title: str
    room_id: str
    index: int
    characters: List[Character]


class Delete3dModelRequest(BaseModel):
    title: str
    room_id: str
    index: int
    character_name: str
