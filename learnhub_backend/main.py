import sys
from fastapi import FastAPI
from .database import db_client
import uvicorn

app = FastAPI()
try:
    db_client.list_database_names()
except:
    sys.exit("Error: Database connection failed")

@app.get("/", status_code=200)
def read_root():
    return {"Hello": "World"}

def start_dev_server():
    uvicorn.run("learnhub_backend.main:app", reload=True)
