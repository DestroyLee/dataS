from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from backend.models import (
    ConfigListResponse, 
    ConfigDetailResponse,
    SyncTaskConfig,
    SaveConfigRequest
)
from backend.services.config_service import ConfigStorage

router = APIRouter(prefix="/api/config", tags=["配置管理"])
config_storage = ConfigStorage()


@router.get("/list", response_model=ConfigListResponse)
async def list_configs():
    """获取配置列表"""
    configs = config_storage.list_configs()
    return ConfigListResponse(configs=configs, total=len(configs))


@router.get("/{config_id}", response_model=ConfigDetailResponse)
async def get_config(config_id: str):
    """获取配置详情"""
    config_data = config_storage.load_config(config_id)
    
    if not config_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 {config_id} 不存在"
        )
    
    return ConfigDetailResponse(**config_data)


@router.post("/save")
async def save_config(request: SaveConfigRequest):
    """保存配置"""
    config_id = config_storage.save_config(
        name=request.name,
        config=request.config.model_dump()
    )
    
    return {
        "message": "配置保存成功",
        "config_id": config_id
    }


@router.put("/{config_id}")
async def update_config(config_id: str, request: SaveConfigRequest):
    """更新配置"""
    success = config_storage.update_config(
        config_id=config_id,
        name=request.name,
        config=request.config.model_dump()
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 {config_id} 不存在"
        )
    
    return {"message": "配置更新成功"}


@router.delete("/{config_id}")
async def delete_config(config_id: str):
    """删除配置"""
    success = config_storage.delete_config(config_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置 {config_id} 不存在"
        )
    
    return {"message": "配置删除成功"}
