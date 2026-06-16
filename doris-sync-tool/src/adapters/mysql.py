import mysql.connector
from typing import List
from src.adapters.base import SourceAdapter, TableMeta, ColumnMeta

class MySQLAdapter(SourceAdapter):
    """MySQL源数据库适配器"""
    
    # MySQL 到 Doris 的类型映射（包含特殊类型）
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
        # 新增特殊类型支持
        'bit': 'BOOLEAN',
        'bool': 'BOOLEAN',
        'year': 'INT',
        'enum': 'STRING',
        'set': 'STRING',
        'blob': 'STRING',
        'tinyblob': 'STRING',
        'mediumblob': 'STRING',
        'longblob': 'STRING',
        'binary': 'STRING',
        'varbinary': 'STRING',
        'geometry': 'STRING',
        'point': 'STRING',
        'linestring': 'STRING',
        'polygon': 'STRING',
    }
    
    # unsigned 类型映射
    UNSIGNED_MAP = {
        'tinyint': 'SMALLINT',  # TINYINT UNSIGNED -> SMALLINT
        'smallint': 'INT',      # SMALLINT UNSIGNED -> INT
        'mediumint': 'INT',     # MEDIUMINT UNSIGNED -> INT
        'int': 'BIGINT',        # INT UNSIGNED -> BIGINT
        'bigint': 'DECIMAL(20,0)',  # BIGINT UNSIGNED -> DECIMAL
    }
    
    def __init__(self, config: dict):
        self.config = config
        self.conn = None
        self.cursor = None
    
    def connect(self) -> None:
        """连接 MySQL 数据库，带错误处理"""
        try:
            self.conn = mysql.connector.connect(
                host=self.config['host'],
                port=self.config.get('port', 3306),
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            raise ConnectionError(f"Failed to connect to MySQL: {e}")
    
    def disconnect(self) -> None:
        """断开数据库连接，带错误处理"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except mysql.connector.Error as e:
            # 记录警告但不抛出异常，因为这是清理操作
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error while disconnecting: {e}")
    
    def get_all_tables(self, database: str) -> List[str]:
        """获取所有表名，带错误处理"""
        try:
            self.cursor.execute("SHOW TABLES")
            return [row[0] for row in self.cursor.fetchall()]
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to get table list from database {database}: {e}")
    
    def get_table_meta(self, table_name: str) -> TableMeta:
        """获取表元数据，带错误处理"""
        try:
            # 获取表结构
            self.cursor.execute(f"DESCRIBE `{table_name}`")
            columns = []
            for row in self.cursor.fetchall():
                col_name = row[0]
                col_type_raw = row[1]
                is_nullable = row[2] == 'YES'
                comment = row[7] if len(row) > 7 else ""
                
                doris_type = self._map_type(col_type_raw)
                columns.append(ColumnMeta(col_name, doris_type, is_nullable, comment))
            
            # 获取数据量
            self.cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            row_count = self.cursor.fetchone()[0]
            
            return TableMeta(table_name, columns, row_count)
        except mysql.connector.Error as e:
            raise RuntimeError(f"Failed to get metadata for table {table_name}: {e}")
    
    def _map_type(self, mysql_type: str) -> str:
        """MySQL 类型转 Doris 类型（支持 unsigned 和特殊类型）"""
        mysql_type_lower = mysql_type.lower().strip()
        
        # 提取基础类型和修饰符
        base_type = mysql_type_lower.split('(')[0].split()[0]
        is_unsigned = 'unsigned' in mysql_type_lower
        
        # 处理带精度的类型
        if mysql_type_lower.startswith('decimal'):
            return mysql_type.upper().replace('UNSIGNED', '').strip()
        if mysql_type_lower.startswith('varchar'):
            size = mysql_type.split('(')[1].rstrip(')').split()[0]
            return f'VARCHAR({size})'
        if mysql_type_lower.startswith('char'):
            size = mysql_type.split('(')[1].rstrip(')').split()[0]
            return f'CHAR({size})'
        if mysql_type_lower.startswith('datetime'):
            # 提取精度
            if '(' in mysql_type:
                precision = mysql_type.split('(')[1].rstrip(')')
                return f'DATETIME({precision})'
            return 'DATETIME'
        if mysql_type_lower.startswith('timestamp'):
            # 提取精度
            if '(' in mysql_type:
                precision = mysql_type.split('(')[1].rstrip(')')
                return f'DATETIME({precision})'
            return 'DATETIME'
        
        # 处理 unsigned 类型
        if is_unsigned and base_type in self.UNSIGNED_MAP:
            return self.UNSIGNED_MAP[base_type]
        
        # 基础类型映射
        doris_type = self.TYPE_MAP.get(base_type, 'STRING')
        
        # 特殊处理 enum 和 set，提取值列表
        if base_type == 'enum':
            # 提取枚举值
            try:
                values = mysql_type[mysql_type.find('('):mysql_type.rfind(')')+1]
                return f'STRING {values}'
            except:
                return 'STRING'
        elif base_type == 'set':
            try:
                values = mysql_type[mysql_type.find('('):mysql_type.rfind(')')+1]
                return f'STRING {values}'
            except:
                return 'STRING'
        
        return doris_type
