from typing import List
from pydantic import BaseModel


class CreateImage360Request(BaseModel):
    title: str
    prompt: str


class CreateScene360Request(BaseModel):
    title: str
    prompts: List[str]


class GetImagesRequest(BaseModel):
    paths: List[str]
