from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    host: str = Field(..., description="数据库主机")
    port: int = Field(default=3306, description="数据库端口")
    user: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    database: str = Field(..., description="数据库名")


class DorisConfig(BaseModel):
    """Doris 目标配置模型"""
    fe_host: str = Field(..., description="FE 主机")
    query_port: int = Field(default=9030, description="查询端口")
    user: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    database: str = Field(..., description="数据库名")


class TableConfig(BaseModel):
    """表配置模型"""
    table_name: str = Field(..., description="表名")
    unique_keys: Optional[List[str]] = Field(default=[], description="唯一键列表")


class SyncTaskConfig(BaseModel):
    """同步任务配置模型"""
    source: DatabaseConfig
    target: DorisConfig
    tables: List[TableConfig]
    defaults: Optional[Dict[str, Any]] = Field(default=None, description="默认配置")


class ConfigListResponse(BaseModel):
    """配置列表响应"""
    configs: List[Dict[str, Any]]
    total: int


class ConfigDetailResponse(BaseModel):
    """配置详情响应"""
    id: str
    name: str
    config: SyncTaskConfig
    created_at: str
    updated_at: str


class TableMetaColumn(BaseModel):
    """表元数据列"""
    name: str
    data_type: str
    nullable: bool
    comment: str = ""


class TableMetaResponse(BaseModel):
    """表元数据响应"""
    table_name: str
    columns: List[TableMetaColumn]
    row_count: int


class TableListRequest(BaseModel):
    """表列表请求"""
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


class TableListResponse(BaseModel):
    """表列表响应"""
    tables: List[str]


class PreviewRequest(BaseModel):
    """预览请求"""
    config: SyncTaskConfig
    table_name: str


class PreviewResponse(BaseModel):
    """预览响应"""
    table_name: str
    ddl_sql: str
    datax_json: str
    bucket_num: int
    distribution_cols: List[str]


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo(BaseModel):
    """任务信息"""
    id: str
    config_id: str
    config_name: str
    status: TaskStatus
    progress: int = 0
    message: str = ""
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskInfo]
    total: int


class TaskExecuteRequest(BaseModel):
    """任务执行请求"""
    config_id: Optional[str] = None
    config: Optional[SyncTaskConfig] = None
    table_names: Optional[List[str]] = None


class TaskLogResponse(BaseModel):
    """任务日志响应"""
    task_id: str
    logs: List[str]
    status: TaskStatus


class SaveConfigRequest(BaseModel):
    """保存配置请求"""
    name: str
    config: SyncTaskConfig
