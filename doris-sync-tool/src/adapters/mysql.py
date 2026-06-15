import mysql.connector
from typing import List
from src.adapters.base import SourceAdapter, TableMeta, ColumnMeta

class MySQLAdapter(SourceAdapter):
    """MySQL源数据库适配器"""
    
    # MySQL到Doris的类型映射
    TYPE_MAP = {
        'tinyint': 'TINYINT',
        'smallint': 'SMALLINT',
        'mediumint': 'INT',
        'int': 'INT',
        'bigint': 'BIGINT',
        'float': 'FLOAT',
        'double': 'DOUBLE',
        'decimal': 'DECIMAL',
        'date': 'DATE',
        'datetime': 'DATETIME',
        'timestamp': 'DATETIME',
        'time': 'TIME',
        'char': 'CHAR',
        'varchar': 'VARCHAR',
        'text': 'STRING',
        'tinytext': 'STRING',
        'mediumtext': 'STRING',
        'longtext': 'STRING',
        'json': 'STRING',
    }
    
    def __init__(self, config: dict):
        self.config = config
        self.conn = None
        self.cursor = None
    
    def connect(self) -> None:
        self.conn = mysql.connector.connect(
            host=self.config['host'],
            port=self.config.get('port', 3306),
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database']
        )
        self.cursor = self.conn.cursor()
    
    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_all_tables(self, database: str) -> List[str]:
        self.cursor.execute("SHOW TABLES")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_table_meta(self, table_name: str) -> TableMeta:
        # 获取表结构
        self.cursor.execute(f"DESCRIBE `{table_name}`")
        columns = []
        for row in self.cursor.fetchall():
            col_name = row[0]
            col_type = row[1].lower().split('(')[0]  # 提取基础类型
            is_nullable = row[2] == 'YES'
            comment = row[7] if len(row) > 7 else ""
            
            doris_type = self._map_type(row[1])
            columns.append(ColumnMeta(col_name, doris_type, is_nullable, comment))
        
        # 获取数据量
        self.cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        row_count = self.cursor.fetchone()[0]
        
        return TableMeta(table_name, columns, row_count)
    
    def _map_type(self, mysql_type: str) -> str:
        """MySQL类型转Doris类型"""
        mysql_type_lower = mysql_type.lower()
        
        # 处理带精度的类型
        if mysql_type_lower.startswith('decimal'):
            return mysql_type.upper()
        if mysql_type_lower.startswith('varchar'):
            size = mysql_type.split('(')[1].rstrip(')')
            return f'VARCHAR({size})'
        if mysql_type_lower.startswith('char'):
            size = mysql_type.split('(')[1].rstrip(')')
            return f'CHAR({size})'
        if mysql_type_lower.startswith('datetime'):
            return 'DATETIME'
        if mysql_type_lower.startswith('timestamp'):
            return 'DATETIME'
        
        # 基础类型映射
        base_type = mysql_type_lower.split('(')[0]
        return self.TYPE_MAP.get(base_type, 'STRING')
