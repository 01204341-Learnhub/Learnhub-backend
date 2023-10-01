from pymongo import MongoClient
from .config import (
    DB_ANNOUNCEMENT_COLLECTION,
    DB_CLASS_COLLECTION,
    DB_COURSE_PROGRESS_COLLECTION,
    DB_TAG_COLLECTION,
    DB_TRANSACTION_COLLECTION,
    MONGODB_URI,
    MONGODB_DB_NAME,
    DB_COURSE_COLLECTION,
    DB_CHAPTER_COLLECTION,
    DB_LESSON_COLLECTION,
    DB_USER_COLLECTION,
    DB_QUIZ_COLLECTION,
    DB_QUIZ_RESULT_COLLECTION,
)


class DB_client(MongoClient):
    def __init__(self, *args, **kwargs):
        super(DB_client, self).__init__(*args, **kwargs)

        self.db = self[MONGODB_DB_NAME]

        # add collection here
        self.course_coll = self.db[DB_COURSE_COLLECTION]
        self.chapter_coll = self.db[DB_CHAPTER_COLLECTION]
        self.lesson_coll = self.db[DB_LESSON_COLLECTION]
        self.announcement_coll = self.db[DB_ANNOUNCEMENT_COLLECTION]
        self.course_progress_coll = self.db[DB_COURSE_PROGRESS_COLLECTION]

        self.class_coll = self.db[DB_CLASS_COLLECTION]

        self.tag_coll = self.db[DB_TAG_COLLECTION]
        self.transaction_coll = self.db[DB_TRANSACTION_COLLECTION]

        self.user_coll = self.db[DB_USER_COLLECTION]

        self.quiz_coll = self.db[DB_QUIZ_COLLECTION]
        self.quiz_result_coll = self.db[DB_QUIZ_RESULT_COLLECTION]


db_client = DB_client(MONGODB_URI)
