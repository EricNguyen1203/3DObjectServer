from typing import Any, Dict, List, Optional

from bson import ObjectId
from Repositories.base_repository import BaseRepository
from Models.image360_entity import Image360Entity
class Image360Repository(BaseRepository):
    
    def __init__(self):
        super().__init__()  
        self._collection_name = "image360"
        self._collection_instance = self._mongo_instance.get_collection(collection_name=self._collection_name)
    
    def insert_one(self, data: Image360Entity):
        result = self._collection_instance.insert_one(data.to_dict())
        print("Inserted ID:", result.inserted_id)
        return result.inserted_id
    
    def insert_many(self, data: List[Image360Entity]):
        inserted_list = [entity.to_dict() for entity in data ]
        result = self._collection_instance.insert_many(inserted_list).inserted_ids
        print("Inserted IDs:", result)    
        return result
    
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
    