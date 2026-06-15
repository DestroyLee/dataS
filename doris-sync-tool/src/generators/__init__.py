from jinja2 import Environment, FileSystemLoader
import os

class DDLGenerator:
    """Doris DDL生成器"""
    
    def __init__(self, template_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template('doris_ddl.j2')
    
    def generate(self, table_meta, unique_keys: list, bucket_num: int, 
                 distribution_cols: list, replication: int = 3) -> str:
        """生成建表SQL"""
        
        # 构建列定义
        columns = []
        for col in table_meta.columns:
            col_def = {
                'name': col.name,
                'type': col.data_type,
                'nullable': col.nullable,
                'comment': col.comment
            }
            columns.append(col_def)
        
        # 渲染模板
        return self.template.render(
            table_name=table_meta.table_name,
            columns=columns,
            unique_keys=unique_keys,
            bucket_num=bucket_num,
            distribution_cols=distribution_cols,
            replication=replication
        )

class DataXGenerator:
    """DataX JSON配置生成器"""
    
    def __init__(self, template_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template('datax_json.j2')
    
    def generate(self, table_meta: str, source_config: dict, target_config: dict,
                 unique_keys: list = None) -> str:
        """生成DataX JSON配置"""
        
        # 构建reader配置
        reader_config = {
            'jdbcUrl': [f"jdbc:mysql://{source_config['host']}:{source_config.get('port', 3306)}/{source_config['database']}"],
            'connection': [{
                'querySql': [f"SELECT * FROM `{table_meta}`"],
                'table': [table_meta]
            }],
            'username': source_config['user'],
            'password': source_config['password']
        }
        
        # 构建writer配置
        writer_config = {
            'jdbcUrl': f"jdbc:mysql://{target_config['fe_host']}:{target_config.get('query_port', 9030)}/{target_config['database']}",
            'username': target_config['user'],
            'password': target_config['password'],
            'table': table_meta,
            'column': ['*'],
            'preSql': [],
            'writeMode': 'insert',
            'batchSize': 1024
        }
        
        # 渲染模板
        return self.template.render(
            table_name=table_meta,
            reader=reader_config,
            writer=writer_config,
            unique_keys=unique_keys or []
        )
