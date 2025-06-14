from typing import Optional
from bson import ObjectId
from Models.models import BaseEntity

class Image360Entity(BaseEntity):
    def __init__(self, title: str, prompt: str, path: Optional[str] = None, room_id: Optional[ObjectId] = None):
        super().__init__()
        self._title = title
        self._prompt = prompt
        self._path = path
        self._room_id = room_id