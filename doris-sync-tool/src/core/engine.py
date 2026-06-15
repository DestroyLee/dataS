import os
import logging
from typing import List
from src.adapters.mysql import MySQLAdapter
from src.strategies.base import AutoBucketStrategy
from src.generators import DDLGenerator, DataXGenerator
from src.core.loader import ConfigLoader
from src.utils.security import ConfigSecurity

logger = logging.getLogger(__name__)

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
        logger.info(f"正在连接源数据库：{self.config['source']['host']}...")
        
        try:
            self.source_adapter.connect()
            
            for table_config in self.config['tables']:
                table_name = table_config['table_name']
                unique_keys = table_config.get('unique_keys', [])
                
                logger.info(f"\n处理表：{table_name}")
                
                # 1. 获取元数据
                logger.info("  - 获取表结构和数据量...")
                table_meta = self.source_adapter.get_table_meta(table_name)
                logger.info(f"    行数：{table_meta.row_count:,}")
                logger.info(f"    列数：{len(table_meta.columns)}")
                
                # 2. 计算分桶策略
                bucket_num = self.bucket_strategy.get_bucket_num(table_meta.row_count)
                dist_cols = self.bucket_strategy.get_distribution_columns(
                    table_meta, 
                    table_config
                )
                replication = self.config.get('defaults', {}).get('replication', 3)
                
                logger.info(f"    分桶数：{bucket_num}")
                logger.info(f"    分布列：{dist_cols}")
                
                # 3. 生成 DDL
                logger.info("  - 生成 Doris 建表 SQL...")
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
                logger.info(f"    已保存：{ddl_file}")
                
                # 4. 生成 DataX 配置
                logger.info("  - 生成 DataX JSON 配置...")
                datax_json = self.datax_generator.generate(
                    table_meta=table_name,
                    source_config=self.config['source'],
                    target_config=self.config['target'],
                    unique_keys=unique_keys
                )
                
                datax_file = os.path.join(datax_output, f"{table_name}.json")
                with open(datax_file, 'w', encoding='utf-8') as f:
                    f.write(datax_json)
                logger.info(f"    已保存：{datax_file}")
            
            logger.info("\n" + "="*50)
            logger.info("✅ 所有任务完成！")
            logger.info(f"📁 DDL 文件目录：{ddl_output}")
            logger.info(f"📁 DataX 配置目录：{datax_output}")
            logger.info("\n下一步操作指引:")
            logger.info("1. 在 Doris 中执行 DDL 文件创建 ODS 表")
            logger.info("2. 使用 DataX 运行生成的 JSON 配置文件进行数据同步")
            logger.info("3. (可选) 将 DataX 任务配置到海豚调度平台")
            
        except Exception as e:
            logger.error(f"执行过程中发生错误：{e}", exc_info=True)
            raise
        finally:
            self.source_adapter.disconnect()
            logger.info("\n已断开数据库连接")
