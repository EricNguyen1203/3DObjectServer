from typing import Optional
from bson import ObjectId
from Models.models import BaseEntity

class Image360Entity(BaseEntity):

    def __init__(
        self,
        title: str,
        prompt: Optional[str] = None,
        path: Optional[str] = None,
        room_id: str = None,
        index: Optional[int] = None,
    ):
        super().__init__()
        self._title = title
        if prompt is not None:
            self._prompt = prompt
        if path is not None:
            self._path = path
        if index is not None:
            self._index = index
        self._room_id = room_id
