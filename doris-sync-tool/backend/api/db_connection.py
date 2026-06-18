from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from backend.models import DatabaseConfig
from backend.services.db_connection_service import DbConnectionStorage

router = APIRouter(prefix="/api/db-connection", tags=["数据库连接管理"])
db_storage = DbConnectionStorage()


@router.get("/list")
async def list_connections():
    """获取数据库连接列表"""
    connections = db_storage.list_connections()
    return {"connections": connections, "total": len(connections)}


@router.get("/{connection_id}")
async def get_connection(connection_id: str):
    """获取数据库连接详情"""
    conn_data = db_storage.load_connection(connection_id)
    
    if not conn_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库连接 {connection_id} 不存在"
        )
    
    return {"id": conn_data["id"], "name": conn_data["name"], "connection": conn_data["connection"]}


@router.post("/save")
async def save_connection(request: dict):
    """保存数据库连接"""
    name = request.get("name")
    connection = request.get("connection")
    
    if not name or not connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要参数"
        )
    
    connection_id = db_storage.save_connection(name=name, connection=connection)
    
    return {
        "message": "数据库连接保存成功",
        "connection_id": connection_id
    }


@router.put("/{connection_id}")
async def update_connection(connection_id: str, request: dict):
    """更新数据库连接"""
    name = request.get("name")
    connection = request.get("connection")
    
    if not name or not connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要参数"
        )
    
    success = db_storage.update_connection(
        connection_id=connection_id,
        name=name,
        connection=connection
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库连接 {connection_id} 不存在"
        )
    
    return {"message": "数据库连接更新成功"}


@router.delete("/{connection_id}")
async def delete_connection(connection_id: str):
    """删除数据库连接"""
    success = db_storage.delete_connection(connection_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"数据库连接 {connection_id} 不存在"
        )
    
    return {"message": "数据库连接删除成功"}


@router.post("/test")
async def test_connection(connection: DatabaseConfig):
    """测试数据库连接"""
    import pymysql
    
    try:
        conn = pymysql.connect(
            host=connection.host,
            port=connection.port,
            user=connection.user,
            password=connection.password,
            database=connection.database,
            connect_timeout=5
        )
        conn.close()
        return {"success": True, "message": "连接成功"}
    except Exception as e:
        return {"success": False, "message": f"连接失败：{str(e)}"}


@router.post("/databases/list")
async def list_databases(connection: DatabaseConfig):
    """获取数据库列表"""
    import pymysql
    
    try:
        conn = pymysql.connect(
            host=connection.host,
            port=connection.port,
            user=connection.user,
            password=connection.password,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute('SHOW DATABASES')
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        databases = [row[0] for row in results]
        return {"success": True, "databases": databases}
    except Exception as e:
        return {"success": False, "message": f"查询失败：{str(e)}"}
