from typing import List
from pydantic import BaseModel


class CreateImage360Request(BaseModel):
    title: str
    prompt: str
    room_id: str
    index: int


class CreateScene360Request(BaseModel):
    title: str
    prompts: List[str]


class GetImagesRequest(BaseModel):
    paths: List[str]
