from pymongo import MongoClient
from .config import MONGODB_URI, MONGODB_DB_NAME

mongo_client = MongoClient(MONGODB_URI)
db_client = mongo_client[MONGODB_DB_NAME]
