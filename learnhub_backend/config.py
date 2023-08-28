from starlette.config import Config

# Load environment variables from .env file
config = Config(".env")

# Get a value from .env file
MONGODB_URI = config("MONGODB_URI", default="mongodb://root:verystrongrootpassword@localhost:27017/?authMechanism=DEFAULT")
MONGODB_DB_NAME = config("MONGODB_DB_NAME", default="LearnHub")

DB_COURSE_COLLECTION = config("DB_COURSE_COLLECTION",default="courses")
DB_CHAPTER_COLLECTION = config("DB_CHAPTER_COLLECTION", default="chapters")
DB_LESSON_COLLECTION = config("DB_LESSON_COLLECTION", default="lessons")
