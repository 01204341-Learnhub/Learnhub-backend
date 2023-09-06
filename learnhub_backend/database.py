from pymongo import MongoClient
from .config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    DB_COURSE_COLLECTION,
    DB_CHAPTER_COLLECTION,
    DB_LESSON_COLLECTION,
    DB_USER_COLLECTION,
)


class DB_client(MongoClient):
    def __init__(self, *args, **kwargs):
        super(DB_client, self).__init__(*args, **kwargs)

        self.db = self[MONGODB_DB_NAME]

        # add collection here
        self.course_coll = self.db[DB_COURSE_COLLECTION]
        self.chapter_coll = self.db[DB_CHAPTER_COLLECTION]
        self.lesson_coll = self.db[DB_LESSON_COLLECTION]
        self.user_coll = self.db[DB_USER_COLLECTION]


db_client = DB_client(MONGODB_URI)