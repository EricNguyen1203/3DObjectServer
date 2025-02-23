
import os

from dotenv import load_dotenv

env = load_dotenv()

class EnvUtil:
    HOST_NAME = os.getenv("SERVER_HOST", "localhost")
    USERNAME = os.getenv("SERVER_USERNAME", "some_username")
    PASSWORD = os.getenv("SERVER_PASSWORD", "funny_password")
    REMOTE_FOLDER = os.getenv("REMOTE_PATH", ".")
    LOCAL_FOLDER =  os.getenv("LOCAL_PATH", ".")
    MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME", "eric")
    MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "You will never get")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "You will never get")

