import sys
from fastapi import FastAPI
import uvicorn

from .database import mongo_client
from .program.router import router as program_router

app = FastAPI()
app.include_router(program_router)


try:
    mongo_client.list_database_names()
except:
    sys.exit("Error: Database connection failed")

@app.get("/", status_code=200)
def read_root():
    return {"Hello": "World"}

def start_dev_server():
    uvicorn.run("learnhub_backend.main:app", reload=True)
