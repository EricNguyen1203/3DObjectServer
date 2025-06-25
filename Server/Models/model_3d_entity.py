from typing import Optional
from Models.models import BaseEntity

class Model3dEntity(BaseEntity):

    def __init__(
        self,
        room_id: str,
        title: str,
        index: int,
        character_name: Optional[str] = None,
        prompt: Optional[str] = None,
        path: Optional[str] = None,
    ):
        self._title = title
        self._index = index
        if prompt is not None:
            self._prompt = prompt
        if path is not None:
            self._path = path
        self._room_id = room_id
        if character_name is not None:
            self._character_name = character_name
