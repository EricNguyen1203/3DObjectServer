from pymongo import MongoClient

from Server.env_setup import EnvUtil


class MongoDBCollections:
    def __init__(self, db_name):
        """Initialize the MongoDB connection and specify the database."""
        uri = f"mongodb://{EnvUtil.MONGO_USERNAME}:{EnvUtil.MONGO_PASSWORD}@localhost:27017/"
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        """Return a collection instance."""
        return self.db[collection_name]

    def insert_one(self, collection_name, data):
        """Insert a single document."""
        collection = self.get_collection(collection_name)
        if collection is None:
            print("not collection found")
        result = collection.insert_one(data)
        print("Inserted ID:", result.inserted_id)
        return result.inserted_id

    def insert_many(self, collection_name, data_list):
        """Insert multiple documents."""
        collection = self.get_collection(collection_name)
        return collection.insert_many(data_list).inserted_ids

    def find_one(self, collection_name, query):
        """Find one document based on a query."""
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_all(self, collection_name, query={}):
        """Find all documents based on a query."""
        collection = self.get_collection(collection_name)
        return list(collection.find(query))

    def update_one(self, collection_name, query, update_data):
        """Update a single document."""
        collection = self.get_collection(collection_name)
        return collection.update_one(query, {"$set": update_data})

    def update_or_insert_one(self, collection_name, query, update_data):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, {"$set": update_data}, upsert=True)

    def update_many(self, collection_name, query, update_data):
        """Update multiple documents."""
        collection = self.get_collection(collection_name)
        return collection.update_many(query, {"$set": update_data})

    def delete_one(self, collection_name, query):
        """Delete a single document."""
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def delete_many(self, collection_name, query):
        """Delete multiple documents."""
        collection = self.get_collection(collection_name)
        return collection.delete_many(query)

    def drop_collection(self, collection_name):
        """Drop an entire collection."""
        collection = self.get_collection(collection_name)
        collection.drop()

