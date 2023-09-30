import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .database import db_client
from .program.router import router as program_router
from .program.course.router import router as course_router
from .student.router import router as student_router
from .teacher.router import router as teacher_router

app = FastAPI()
app.include_router(program_router)
app.include_router(course_router)
app.include_router(student_router)
app.include_router(teacher_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    db_client.list_database_names()
except:
    sys.exit("Error: Database connection failed")


@app.get("/", status_code=200)
def read_root():
    return {"Hello": "World"}


def start_dev_server():
    uvicorn.run("learnhub_backend.main:app", reload=True)
