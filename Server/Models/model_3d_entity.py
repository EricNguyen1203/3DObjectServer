from Models.models import BaseEntity

class Model3dEntity(BaseEntity):
    def __init__(self, title: str, prompt: str, path: str):
        super().__init__()
        self._title = title
        self._prompt = prompt
        self._path = path
            
    