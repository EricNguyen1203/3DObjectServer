from typing import List, Optional
from Models.models import BaseEntity

class StoryEntity(BaseEntity):
    def __init__(self, title: str, room_id: str, descriptions: Optional[List[str]] = None):
      self._title = title
      self._room_id = room_id
      if descriptions is not None:
        self._descriptions = descriptions