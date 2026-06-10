from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.DataBase_connect.database import Base,engine

import uvicorn

from app.routers import Interview_websocket, check_Resume, user_router, question_router, interview_router, ai_router, \
    download_router, preview_router

#最终代码中注释了全部的非报错信息提示的控制台输出，降低服务器压力，尽可能提高运行效率，避免不必要的控制台输出提示

Base.metadata.create_all(bind=engine)
app=FastAPI()

#配置CORS，允许前端访问
origins=[
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(Interview_websocket.router, prefix="/interview", tags=["interview"])
app.include_router(check_Resume.router, prefix="/interview", tags=["interview"])

# 注册用户管理路由
app.include_router(user_router.router, prefix="/api/users", tags=["用户管理"])

# 注册面试题目管理路由
app.include_router(question_router.router, prefix="/api/questions", tags=["面试题目管理"])

# 注册面试与评测路由
app.include_router(interview_router.router, prefix="/api/interview", tags=["模拟面试与评测"])

# 注册 AI 助手路由
app.include_router(ai_router.router, prefix="/api/ai", tags=["AI助手"])

app.include_router(download_router.router, prefix="/api/download", tags=["文件下载"])

app.include_router(preview_router.router, prefix="/api/preview", tags=["文件预览"])


@app.get("/", status_code=200)
async def root():
    return HTMLResponse("<h1>欢迎进入模拟面试服务系统<h1>")


#uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
