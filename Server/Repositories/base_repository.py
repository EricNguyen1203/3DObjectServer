from abc import ABC, abstractmethod
from database import MongoDBCollections

class BaseRepository(ABC):
    def __init__(self):
        self._mongo_instance = MongoDBCollections("thesis2025")
    
    @abstractmethod
    def insert_one(self, data):
        pass
    
    @abstractmethod
    def insert_many(self, data: list):
        pass
    
    @abstractmethod
    def load_one(self, query: dict):
        pass
    
    @abstractmethod
    def load_many(self, query: dict):
        pass