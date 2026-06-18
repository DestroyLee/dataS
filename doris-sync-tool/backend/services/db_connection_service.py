import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class DbConnectionStorage:
    """数据库连接存储服务"""
    
    def __init__(self, storage_dir: str = "./backend/data/db_connections"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_connection_path(self, connection_id: str) -> Path:
        return self.storage_dir / f"{connection_id}.json"
    
    def save_connection(self, name: str, connection: Dict[str, Any]) -> str:
        """保存数据库连接"""
        connection_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        # 不保存密码到文件中（安全考虑），或者可以加密存储
        connection_data = {
            "id": connection_id,
            "name": name,
            "connection": {
                "host": connection.get("host", ""),
                "port": connection.get("port", 3306),
                "user": connection.get("user", ""),
                "password": connection.get("password", ""),  # 暂时明文存储，生产环境应加密
                "database": connection.get("database", "")
            },
            "created_at": now,
            "updated_at": now
        }
        
        connection_path = self._get_connection_path(connection_id)
        with open(connection_path, 'w', encoding='utf-8') as f:
            json.dump(connection_data, f, indent=2, ensure_ascii=False)
        
        return connection_id
    
    def update_connection(self, connection_id: str, name: str, connection: Dict[str, Any]) -> bool:
        """更新数据库连接"""
        connection_path = self._get_connection_path(connection_id)
        
        if not connection_path.exists():
            return False
        
        now = datetime.now().isoformat()
        old_data = self.load_connection(connection_id)
        
        connection_data = {
            "id": connection_id,
            "name": name,
            "connection": {
                "host": connection.get("host", ""),
                "port": connection.get("port", 3306),
                "user": connection.get("user", ""),
                "password": connection.get("password", old_data["connection"].get("password", "")),
                "database": connection.get("database", "")
            },
            "created_at": old_data["created_at"],
            "updated_at": now
        }
        
        with open(connection_path, 'w', encoding='utf-8') as f:
            json.dump(connection_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def load_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """加载数据库连接"""
        connection_path = self._get_connection_path(connection_id)
        
        if not connection_path.exists():
            return None
        
        with open(connection_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_connection(self, connection_id: str) -> bool:
        """删除数据库连接"""
        connection_path = self._get_connection_path(connection_id)
        
        if not connection_path.exists():
            return False
        
        os.remove(connection_path)
        return True
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """列出所有数据库连接"""
        connections = []
        
        for conn_file in self.storage_dir.glob("*.json"):
            with open(conn_file, 'r', encoding='utf-8') as f:
                conn_data = json.load(f)
                # 返回基本信息，密码字段脱敏
                connections.append({
                    "id": conn_data["id"],
                    "name": conn_data["name"],
                    "host": conn_data["connection"]["host"],
                    "port": conn_data["connection"]["port"],
                    "user": conn_data["connection"]["user"],
                    "database": conn_data["connection"]["database"],
                    "created_at": conn_data["created_at"],
                    "updated_at": conn_data["updated_at"]
                })
        
        return sorted(connections, key=lambda x: x["updated_at"], reverse=True)
    
    def get_connection_detail(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """获取连接详情（包含密码）"""
        connection_path = self._get_connection_path(connection_id)
        
        if not connection_path.exists():
            return None
        
        with open(connection_path, 'r', encoding='utf-8') as f:
            return json.load(f)
