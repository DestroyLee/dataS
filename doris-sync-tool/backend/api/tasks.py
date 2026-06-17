from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, Any
import asyncio
import uuid
from datetime import datetime

from backend.models import (
    TaskExecuteRequest,
    TaskListResponse,
    TaskInfo,
    TaskStatus,
    TaskLogResponse
)
from backend.services.task_service import TaskRunner

router = APIRouter(prefix="/api/tasks", tags=["任务执行"])

# 内存中的任务存储（生产环境建议使用 Redis 或数据库）
active_tasks: Dict[str, Dict[str, Any]] = {}
task_logs: Dict[str, list] = {}

task_runner = TaskRunner()


async def run_task_background(task_id: str, config: Dict[str, Any], table_names: list):
    """后台运行任务"""
    try:
        active_tasks[task_id]["status"] = TaskStatus.RUNNING
        active_tasks[task_id]["started_at"] = datetime.now().isoformat()
        task_logs[task_id].append(f"[{datetime.now().strftime('%H:%M:%S')}] 任务开始执行")
        
        async def progress_callback(stage: str, message: str, progress: int = 0):
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_msg = f"[{timestamp}] {message} (进度：{progress}%)"
            task_logs[task_id].append(log_msg)
            active_tasks[task_id]["message"] = message
            active_tasks[task_id]["progress"] = progress
        
        result = await task_runner.execute_sync(
            config=config,
            table_names=table_names,
            progress_callback=progress_callback
        )
        
        active_tasks[task_id]["status"] = TaskStatus.SUCCESS
        active_tasks[task_id]["finished_at"] = datetime.now().isoformat()
        active_tasks[task_id]["message"] = f"成功：{result['success_count']} 表，失败：{result['failed_count']} 表"
        active_tasks[task_id]["progress"] = 100
        task_logs[task_id].append(f"[{datetime.now().strftime('%H:%M:%S')}] 任务执行完成")
        
    except Exception as e:
        active_tasks[task_id]["status"] = TaskStatus.FAILED
        active_tasks[task_id]["finished_at"] = datetime.now().isoformat()
        active_tasks[task_id]["message"] = str(e)
        task_logs[task_id].append(f"[{datetime.now().strftime('%H:%M:%S')}] 任务执行失败：{str(e)}")


@router.post("/execute")
async def execute_task(request: TaskExecuteRequest, background_tasks: BackgroundTasks):
    """执行同步任务"""
    task_id = str(uuid.uuid4())[:8]
    
    # 如果是使用保存的配置
    if request.config_id:
        from backend.services.config_service import ConfigStorage
        config_storage = ConfigStorage()
        config_data = config_storage.load_config(request.config_id)
        
        if not config_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"配置 {request.config_id} 不存在"
            )
        
        config = config_data["config"]
        config_name = config_data["name"]
        table_names = request.table_names or [t["table_name"] for t in config.get("tables", [])]
    
    # 如果是临时配置
    elif request.config:
        config = request.config.model_dump()
        config_name = "临时任务"
        table_names = request.table_names or [t["table_name"] for t in config.get("tables", [])]
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供 config_id 或 config"
        )
    
    # 初始化任务状态
    now = datetime.now().isoformat()
    active_tasks[task_id] = {
        "id": task_id,
        "config_id": request.config_id or "temp",
        "config_name": config_name,
        "status": TaskStatus.PENDING,
        "progress": 0,
        "message": "任务已提交，等待执行",
        "created_at": now,
        "started_at": None,
        "finished_at": None
    }
    
    task_logs[task_id] = [f"[{now}] 任务已创建"]
    
    # 启动后台任务
    background_tasks.add_task(run_task_background, task_id, config, table_names)
    
    return {
        "message": "任务已提交",
        "task_id": task_id
    }


@router.get("/list", response_model=TaskListResponse)
async def list_tasks():
    """获取任务列表"""
    tasks = [
        TaskInfo(**task_data)
        for task_data in active_tasks.values()
    ]
    
    return TaskListResponse(
        tasks=tasks,
        total=len(tasks)
    )


@router.get("/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    if task_id not in active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    return active_tasks[task_id]


@router.get("/{task_id}/logs", response_model=TaskLogResponse)
async def get_task_logs(task_id: str):
    """获取任务日志"""
    if task_id not in active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    return TaskLogResponse(
        task_id=task_id,
        logs=task_logs.get(task_id, []),
        status=active_tasks[task_id]["status"]
    )


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    if task_id not in active_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    if active_tasks[task_id]["status"] in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务已完成，无法取消"
        )
    
    active_tasks[task_id]["status"] = TaskStatus.CANCELLED
    active_tasks[task_id]["finished_at"] = datetime.now().isoformat()
    active_tasks[task_id]["message"] = "任务已取消"
    task_logs[task_id].append(f"[{datetime.now().strftime('%H:%M:%S')}] 任务已取消")
    
    return {"message": "任务已取消"}
