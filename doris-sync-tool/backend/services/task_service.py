import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 配置日志 - 输出到 doris-sync-tool/logs 目录
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "backend.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

from src.adapters.mysql import MySQLAdapter
from src.strategies.base import AutoBucketStrategy
from src.generators import DDLGenerator, DataXGenerator

logger = logging.getLogger(__name__)


class TaskRunner:
    """任务执行器"""
    
    def __init__(self, template_dir: str = "./config/templates"):
        self.template_dir = template_dir
        self.bucket_strategy = AutoBucketStrategy()
        self.ddl_generator = DDLGenerator(template_dir)
        self.datax_generator = DataXGenerator(template_dir)
        logger.info(f"TaskRunner initialized with template_dir: {template_dir}")
    
    async def execute_preview(
        self, 
        config: Dict[str, Any], 
        table_name: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """执行预览"""
        logger.info(f"Starting preview for table: {table_name}")
        logger.debug(f"Config: {config}")
        
        source_config = config.get('source')
        if not source_config:
            logger.error("Missing 'source' in config")
            raise ValueError("配置中缺少 'source' 字段")
        
        # 连接数据库
        adapter = MySQLAdapter(source_config)
        
        try:
            if progress_callback:
                await progress_callback("connecting", "正在连接数据库...")
            
            logger.info(f"Connecting to MySQL: {source_config.get('host')}:{source_config.get('port')}/{source_config.get('database')}")
            adapter.connect()
            
            if progress_callback:
                await progress_callback("fetching_meta", f"获取表 {table_name} 元数据...")
            
            # 获取元数据
            logger.info(f"Fetching metadata for table: {table_name}")
            table_meta = adapter.get_table_meta(table_name)
            
            # 计算分桶策略
            tables_config = config.get('tables') or []
            table_config = None
            for tc in tables_config:
                if isinstance(tc, dict) and tc.get('table_name') == table_name:
                    table_config = tc
                    break
                elif hasattr(tc, 'table_name') and tc.table_name == table_name:
                    table_config = tc
                    break
            
            unique_keys = []
            if table_config:
                if isinstance(table_config, dict):
                    unique_keys = table_config.get('unique_keys') or []
                else:
                    unique_keys = getattr(table_config, 'unique_keys', None) or []
            
            logger.info(f"Using unique_keys: {unique_keys}")
            
            bucket_num = self.bucket_strategy.get_bucket_num(table_meta.row_count)
            dist_cols = self.bucket_strategy.get_distribution_columns(
                table_meta,
                {"table_name": table_name, "unique_keys": unique_keys}
            )
            replication = (config.get('defaults') or {}).get('replication', 3)
            logger.info(f"Bucket num: {bucket_num}, Distribution cols: {dist_cols}, Replication: {replication}")
            
            if progress_callback:
                await progress_callback("generating_ddl", "生成 DDL SQL...")
            
            # 生成 DDL
            ddl_sql = self.ddl_generator.generate(
                table_meta=table_meta,
                unique_keys=[],
                bucket_num=bucket_num,
                distribution_cols=dist_cols,
                replication=replication
            )
            
            if progress_callback:
                await progress_callback("generating_datax", "生成 DataX 配置...")
            
            # 生成 DataX JSON
            target_config = config.get('target')
            if not target_config:
                logger.error("Missing 'target' in config")
                raise ValueError("配置中缺少 'target' 字段")
            
            logger.info(f"Generating DataX JSON for target: {target_config.get('fe_host')}:{target_config.get('query_port')}/{target_config.get('database')}")
            datax_json = self.datax_generator.generate(
                table_meta=table_name,
                source_config=source_config,
                target_config=target_config,
                unique_keys=unique_keys
            )
            
            if progress_callback:
                await progress_callback("complete", "预览生成完成")
            
            logger.info(f"Preview generated successfully for table: {table_name}")
            return {
                "table_name": table_name,
                "ddl_sql": ddl_sql,
                "datax_json": datax_json,
                "bucket_num": bucket_num,
                "distribution_cols": dist_cols,
                "row_count": table_meta.row_count,
                "columns": [
                    {
                        "name": col.name,
                        "data_type": col.data_type,
                        "nullable": col.nullable,
                        "comment": col.comment
                    }
                    for col in table_meta.columns
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}", exc_info=True)
            raise
        finally:
            adapter.disconnect()
            logger.info("Database connection closed")
    
    async def execute_sync(
        self,
        config: Dict[str, Any],
        table_names: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """执行同步任务"""
        if table_names is None:
            table_names = [t['table_name'] for t in config['tables']]
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"./output/{timestamp}"
        
        results = []
        errors = []
        
        source_config = config['source']
        adapter = MySQLAdapter(source_config)
        
        try:
            if progress_callback:
                await progress_callback("connecting", "正在连接数据库...", 0)
            
            adapter.connect()
            
            total_tables = len(table_names)
            
            for idx, table_name in enumerate(table_names):
                try:
                    if progress_callback:
                        await progress_callback(
                            "processing", 
                            f"处理表 {table_name} ({idx+1}/{total_tables})",
                            int((idx / total_tables) * 100)
                        )
                    
                    # 获取元数据
                    table_meta = adapter.get_table_meta(table_name)
                    
                    # 计算分桶策略
                    bucket_num = self.bucket_strategy.get_bucket_num(table_meta.row_count)
                    dist_cols = self.bucket_strategy.get_distribution_columns(
                        table_meta,
                        {"table_name": table_name, "unique_keys": []}
                    )
                    replication = (config.get('defaults') or {}).get('replication', 3)
                    
                    # 生成 DDL
                    ddl_sql = self.ddl_generator.generate(
                        table_meta=table_meta,
                        unique_keys=[],
                        bucket_num=bucket_num,
                        distribution_cols=dist_cols,
                        replication=replication
                    )
                    
                    # 生成 DataX JSON
                    datax_json = self.datax_generator.generate(
                        table_meta=table_name,
                        source_config=source_config,
                        target_config=config['target'],
                        unique_keys=[]
                    )
                    
                    results.append({
                        "table_name": table_name,
                        "status": "success",
                        "row_count": table_meta.row_count,
                        "bucket_num": bucket_num
                    })
                    
                except Exception as e:
                    error_msg = f"处理表 {table_name} 失败：{str(e)}"
                    logger.error(error_msg)
                    errors.append({
                        "table_name": table_name,
                        "error": str(e)
                    })
            
            if progress_callback:
                await progress_callback("complete", "任务执行完成", 100)
            
            return {
                "results": results,
                "errors": errors,
                "output_dir": output_dir,
                "success_count": len(results),
                "failed_count": len(errors)
            }
            
        finally:
            adapter.disconnect()
