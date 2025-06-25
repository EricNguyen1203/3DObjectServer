from typing import List, Optional, Tuple
from Models.models import BaseEntity

class CharacterDescriptionEntity(BaseEntity):
    def __init__(
        self, 
        title: str,
        room_id: str,
        index: int,
        descriptions: Optional[List[List[Tuple[str, str]]]] = None
    ):
      self._title = title
      self._room_id = room_id
      self._index = index
      if descriptions is not None:
        self._descriptions = descriptions