from fastapi import FastAPI
from routers.tasks import create_task as task_router

app = FastAPI()

app.include_router(task_router)