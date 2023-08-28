from starlette.config import Config

# Load environment variables from .env file
config = Config(".env")

# Get a value from .env file
MONGODB_URI = config("MONGODB_URI", default="mongodb://root:verystrongrootpassword@localhost:27017/?authMechanism=DEFAULT")
MONGODB_DB_NAME = config("MONGODB_DB_NAME", default="LearnHub")
