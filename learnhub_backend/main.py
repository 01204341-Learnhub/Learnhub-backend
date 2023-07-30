from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/", status_code=200)
def read_root():
    return {"Hello": "World"}

def start_dev_server():
    uvicorn.run("learnhub_backend.main:app", reload=True)
