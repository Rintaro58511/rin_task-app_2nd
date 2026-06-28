from fastapi import FastAPI
#from routers.tasks import router as task_router
from routers.user import router as user_router 

app = FastAPI(
    title="タスク管理 & ユーザー認証 API",
    description="FastAPI + PostgreSQL で構築した、認証機能付きのタスク管理システムです。"
)

app.include_router(user_router, tags=["User (ユーザー認証)"])

#app.include_router(task_router, tags=["Tasks (タスク管理)"])

@app.get("/")
def read_root():
    return {"message": "APIは正常に起動しています。 /docs にアクセスしてください。"}