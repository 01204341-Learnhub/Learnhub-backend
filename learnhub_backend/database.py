from pymongo import MongoClient
from .config import MONGODB_URI, MONGODB_DB_NAME, DB_COURSE_COLLECTION, DB_CHAPTER_COLLECTION, DB_LESSON_COLLECTION



class Mongodb_client(MongoClient):
    def __init__(self, *args, **kwargs):
        super(Mongodb_client, self).__init__(*args, **kwargs)

        self.db = self[MONGODB_DB_NAME] 

        # add collection here
        self.course_coll = self.db[DB_COURSE_COLLECTION]
        self.chapter_coll = self[DB_CHAPTER_COLLECTION]
        self.lesson_coll = self[DB_LESSON_COLLECTION]


db_client = Mongodb_client(MONGODB_URI)
