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