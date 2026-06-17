from fastapi import APIRouter, HTTPException, status
from backend.models import (
    TableListRequest,
    TableListResponse,
    TableMetaResponse,
    PreviewRequest,
    PreviewResponse
)
from backend.services.task_service import TaskRunner

router = APIRouter(prefix="/api/preview", tags=["预览功能"])
task_runner = TaskRunner()


@router.post("/tables/discover", response_model=TableListResponse)
async def discover_tables(request: TableListRequest):
    """发现 MySQL 表列表"""
    from src.adapters.mysql import MySQLAdapter
    
    adapter = MySQLAdapter({
        "host": request.host,
        "port": request.port,
        "user": request.user,
        "password": request.password,
        "database": request.database
    })
    
    try:
        adapter.connect()
        tables = adapter.get_all_tables(request.database)
        return TableListResponse(tables=tables)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接数据库失败：{str(e)}"
        )
    finally:
        adapter.disconnect()


@router.post("/tables/{table_name}/meta", response_model=TableMetaResponse)
async def get_table_meta(table_name: str, request: TableListRequest):
    """获取表元数据"""
    from src.adapters.mysql import MySQLAdapter
    
    adapter = MySQLAdapter({
        "host": request.host,
        "port": request.port,
        "user": request.user,
        "password": request.password,
        "database": request.database
    })
    
    try:
        adapter.connect()
        table_meta = adapter.get_table_meta(table_name)
        
        return TableMetaResponse(
            table_name=table_name,
            columns=[
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "nullable": col.nullable,
                    "comment": col.comment
                }
                for col in table_meta.columns
            ],
            row_count=table_meta.row_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表元数据失败：{str(e)}"
        )
    finally:
        adapter.disconnect()


@router.post("/ddl", response_model=PreviewResponse)
async def preview_ddl(request: PreviewRequest):
    """预览 DDL SQL"""
    try:
        result = await task_runner.execute_preview(
            config=request.config.model_dump(),
            table_name=request.table_name
        )
        
        return PreviewResponse(
            table_name=result["table_name"],
            ddl_sql=result["ddl_sql"],
            datax_json=result["datax_json"],
            bucket_num=result["bucket_num"],
            distribution_cols=result["distribution_cols"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"预览生成失败：{str(e)}"
        )
