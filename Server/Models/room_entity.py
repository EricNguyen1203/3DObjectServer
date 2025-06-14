from Models.models import BaseEntity

class RoomEntity(BaseEntity):
    def __init__(self, name):
      self._name = name