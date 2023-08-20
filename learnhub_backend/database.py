from pymongo import MongoClient
from .config import MONGODB_URI

db_client = MongoClient(MONGODB_URI)
