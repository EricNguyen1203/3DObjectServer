import json

from pydantic import BaseModel


class ModelInfo:
    def __int__(self):
        self.max_face_num=10000
        self.size = "medium"
        self.color = "dark"
        self.material = "normal"

    def to_json(self) -> str:
        """Convert the object to a JSON string."""
        return json.dumps(self.__dict__)  # Convert object attributes to JSON
    def to_dict(self) -> dict:
        return self.__dict__

class PromptRequest(BaseModel):
    prompt: str

class GetZipModelRequest(BaseModel):
    model_id: str


class Model3D:
    model: bytes
    texture: str
    mtl: bytes

    def __init__(self, model: bytes, texture: str, mtl: bytes):
        self.model = model
        self.texture = texture
        self.mtl = mtl

class LLMJsonParseRequest(BaseModel):
    prompt: str

class SaveObjRequest(BaseModel):
    model_param: str
    room_name: str
    room_params: dict
