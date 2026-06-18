from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.api import config_router, preview_router, tasks_router, db_connection_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Doris Sync Tool API",
    description="MySQL 到 Doris 数据同步工具 Web API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(config_router)
app.include_router(preview_router)
app.include_router(tasks_router)
app.include_router(db_connection_router)


@app.get("/")
async def root():
    return {
        "message": "欢迎使用 Doris Sync Tool API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
