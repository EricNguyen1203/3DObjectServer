from typing import List
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Create3dModelRequest(BaseModel):
    title: str
    prompt: List[str]
