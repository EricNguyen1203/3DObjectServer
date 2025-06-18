from typing import Optional
from Models.models import BaseEntity

class Model3dEntity(BaseEntity):

    def __init__(
        self,
        room_id: str,
        title: str,
        character_name: str,
        index: int,
        prompt: Optional[str] = None,
        path: Optional[str] = None,
    ):
        super().__init__()
        self._title = title
        self._prompt = prompt
        self._path = path
        self._room_id = room_id
        self._character_name = character_name
        self._index = index
