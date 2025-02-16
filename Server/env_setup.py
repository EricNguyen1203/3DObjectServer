
import os

from dotenv import load_dotenv

env = load_dotenv()

class EnvUtil:
    HOST_NAME = os.getenv("SERVER_HOST", "localhost")
    USERNAME = os.getenv("SERVER_USERNAME", "some_username")
    PASSWORD = os.getenv("SERVER_PASSWORD", "funny_password")
    REMOTE_FOLDER = os.getenv("REMOTE_PATH", ".")
    LOCAL_FOLDER =  os.getenv("LOCAL_PATH", ".")
