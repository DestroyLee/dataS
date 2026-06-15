import os
from typing import List
from src.adapters.mysql import MySQLAdapter
from src.strategies.base import AutoBucketStrategy
from src.generators import DDLGenerator, DataXGenerator
from src.core.loader import ConfigLoader

class SyncEngine:
    """同步流程核心引擎"""
    
    def __init__(self, config: dict, template_dir: str):
        self.config = config
        self.template_dir = template_dir
        self.source_adapter = MySQLAdapter(config['source'])
        self.bucket_strategy = AutoBucketStrategy()
        self.ddl_generator = DDLGenerator(template_dir)
        self.datax_generator = DataXGenerator(template_dir)
    
    def execute(self, output_dir: str):
        """执行完整同步流程"""
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        ddl_output = os.path.join(output_dir, 'ddl')
        datax_output = os.path.join(output_dir, 'datax')
        os.makedirs(ddl_output, exist_ok=True)
        os.makedirs(datax_output, exist_ok=True)
        
        # 连接源数据库
        print(f"正在连接源数据库：{self.config['source']['host']}...")
        self.source_adapter.connect()
        
        try:
            for table_config in self.config['tables']:
                table_name = table_config['table_name']
                unique_keys = table_config.get('unique_keys', [])
                
                print(f"\n处理表：{table_name}")
                
                # 1. 获取元数据
                print("  - 获取表结构和数据量...")
                table_meta = self.source_adapter.get_table_meta(table_name)
                print(f"    行数：{table_meta.row_count:,}")
                print(f"    列数：{len(table_meta.columns)}")
                
                # 2. 计算分桶策略
                bucket_num = self.bucket_strategy.get_bucket_num(table_meta.row_count)
                dist_cols = self.bucket_strategy.get_distribution_columns(
                    table_meta, 
                    table_config
                )
                replication = self.config.get('defaults', {}).get('replication', 3)
                
                print(f"    分桶数：{bucket_num}")
                print(f"    分布列：{dist_cols}")
                
                # 3. 生成DDL
                print("  - 生成Doris建表SQL...")
                ddl_sql = self.ddl_generator.generate(
                    table_meta=table_meta,
                    unique_keys=unique_keys,
                    bucket_num=bucket_num,
                    distribution_cols=dist_cols,
                    replication=replication
                )
                
                ddl_file = os.path.join(ddl_output, f"{table_name}.sql")
                with open(ddl_file, 'w', encoding='utf-8') as f:
                    f.write(ddl_sql)
                print(f"    已保存：{ddl_file}")
                
                # 4. 生成DataX配置
                print("  - 生成DataX JSON配置...")
                datax_json = self.datax_generator.generate(
                    table_meta=table_name,
                    source_config=self.config['source'],
                    target_config=self.config['target'],
                    unique_keys=unique_keys
                )
                
                datax_file = os.path.join(datax_output, f"{table_name}.json")
                with open(datax_file, 'w', encoding='utf-8') as f:
                    f.write(datax_json)
                print(f"    已保存：{datax_file}")
            
            print("\n" + "="*50)
            print("✅ 所有任务完成！")
            print(f"📁 DDL文件目录：{ddl_output}")
            print(f"📁 DataX配置目录：{datax_output}")
            print("\n下一步操作指引:")
            print("1. 在Doris中执行DDL文件创建ODS表")
            print("2. 使用DataX运行生成的JSON配置文件进行数据同步")
            print("3. (可选) 将DataX任务配置到海豚调度平台")
            
        finally:
            self.source_adapter.disconnect()
            print("\n已断开数据库连接")
