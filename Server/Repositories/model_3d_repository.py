from typing import Any, Dict, List, Optional

from bson import ObjectId
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
        if len(inserted_list) == 0:
            return
        print(inserted_list)
        ids = self._collection_instance.insert_many(inserted_list).inserted_ids
        return ids

    def load_one(self, query: dict) -> Optional[Dict[str, Any]]:
        """
        Load a single document from image360 collection
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            Dictionary representation of the document or None if not found
        """
        result = self._collection_instance.find_one(query)
        if result is None or len(result) == 0:
            return None
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in result and isinstance(result['_id'], ObjectId):
            result['_id'] = str(result['_id'])
            
        return result

    def load_many(self, query: dict) -> List[Dict[str, Any]]:
        """
        Load multiple documents from MongoDB
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            List of dictionary representations of documents, empty list if none found
        """
        cursor = self._collection_instance.find(query)
        
        results = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if '_id' in result and isinstance(result['_id'], ObjectId):
                result['_id'] = str(result['_id'])
                
        return results
