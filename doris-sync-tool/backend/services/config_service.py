import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class ConfigStorage:
    """配置存储服务"""
    
    def __init__(self, storage_dir: str = "./backend/data/configs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_config_path(self, config_id: str) -> Path:
        return self.storage_dir / f"{config_id}.json"
    
    def save_config(self, name: str, config: Dict[str, Any]) -> str:
        """保存配置"""
        config_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        config_data = {
            "id": config_id,
            "name": name,
            "config": config,
            "created_at": now,
            "updated_at": now
        }
        
        config_path = self._get_config_path(config_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return config_id
    
    def update_config(self, config_id: str, name: str, config: Dict[str, Any]) -> bool:
        """更新配置"""
        config_path = self._get_config_path(config_id)
        
        if not config_path.exists():
            return False
        
        now = datetime.now().isoformat()
        config_data = {
            "id": config_id,
            "name": name,
            "config": config,
            "created_at": self.load_config(config_id)["created_at"],
            "updated_at": now
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def load_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """加载配置"""
        config_path = self._get_config_path(config_id)
        
        if not config_path.exists():
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_config(self, config_id: str) -> bool:
        """删除配置"""
        config_path = self._get_config_path(config_id)
        
        if not config_path.exists():
            return False
        
        os.remove(config_path)
        return True
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """列出所有配置"""
        configs = []
        
        for config_file in self.storage_dir.glob("*.json"):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 只返回基本信息，不返回完整配置
                configs.append({
                    "id": config_data["id"],
                    "name": config_data["name"],
                    "created_at": config_data["created_at"],
                    "updated_at": config_data["updated_at"]
                })
        
        return sorted(configs, key=lambda x: x["updated_at"], reverse=True)
