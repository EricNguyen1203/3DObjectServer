from typing import List, Optional, Tuple

from pydantic import BaseModel
from Models.models import BaseEntity


class CharacterDialogue(BaseModel):
    character_name: str
    dialogues: List[str]


class DialogueEntity(BaseEntity):

    def __init__(
        self,
        title: str,
        room_id: str,
        index: int,
        character_dialouges: Optional[List[CharacterDialogue]] = None,
    ):
        self._title = title
        self._room_id = room_id
        self._index = index
        if character_dialouges is not None:
            self._character_dialouges = character_dialouges
