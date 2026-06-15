from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ColumnMeta:
    """列元数据"""
    def __init__(self, name: str, data_type: str, nullable: bool = True, comment: str = ""):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.comment = comment

class TableMeta:
    """表元数据"""
    def __init__(self, table_name: str, columns: List[ColumnMeta], row_count: int = 0):
        self.table_name = table_name
        self.columns = columns
        self.row_count = row_count

class SourceAdapter(ABC):
    """源数据库适配器抽象基类"""
    
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def get_table_meta(self, table_name: str) -> TableMeta:
        """获取表结构和数据量"""
        pass
    
    @abstractmethod
    def get_all_tables(self, database: str) -> List[str]:
        """获取数据库所有表名"""
        pass
