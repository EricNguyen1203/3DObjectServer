from typing import List, Optional
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
        position: Optional[List[str]] = None,
        scale: Optional[List[str]] = None,
        rotation: Optional[List[str]] = None,
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
        if position is not None:
            self._position = position
        if scale is not None:
            self._scale = scale
        if rotation is not None:
            self._rotation = rotation
