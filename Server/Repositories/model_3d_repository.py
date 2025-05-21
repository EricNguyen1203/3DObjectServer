from typing import List
from database import MongoDBCollections
from Repositories.base_repository import BaseRepository
from Models.model_3d_entity import Model3dEntity

class Model3dRepository(BaseRepository):
    def __init__(self):
        super().__init__()  
        self._collection_name = "model3d"
        self._collection_instance = self._mongo_instance.get_collection(collection_name=self._collection_name)
    
    def insert_one(self, data: Model3dEntity):
        result = self._collection_instance.insert_one(data.to_dict())
        print("Inserted ID:", result.inserted_id)
        return result.inserted_id
    
    def insert_many(self, data: List[Model3dEntity]):
        inserted_list = [entity.to_dict() for entity in data ]
        return self._collection_instance.insert_many(inserted_list).inserted_ids
    
    def load_one(self, query: dict) -> dict:
        return self._collection_instance.find_one(query)

    def load_many(self, query: dict) -> List[dict]:
        return list(self._collection_instance.find(query))