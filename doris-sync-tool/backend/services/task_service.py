import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
    
    async def execute_preview(
        self, 
        config: Dict[str, Any], 
        table_name: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """执行预览"""
        source_config = config['source']
        
        # 连接数据库
        adapter = MySQLAdapter(source_config)
        
        try:
            if progress_callback:
                await progress_callback("connecting", "正在连接数据库...")
            
            adapter.connect()
            
            if progress_callback:
                await progress_callback("fetching_meta", f"获取表 {table_name} 元数据...")
            
            # 获取元数据
            table_meta = adapter.get_table_meta(table_name)
            
            # 计算分桶策略
            bucket_num = self.bucket_strategy.get_bucket_num(table_meta.row_count)
            dist_cols = self.bucket_strategy.get_distribution_columns(
                table_meta,
                {"table_name": table_name, "unique_keys": []}
            )
            replication = config.get('defaults', {}).get('replication', 3)
            
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
            datax_json = self.datax_generator.generate(
                table_meta=table_name,
                source_config=source_config,
                target_config=config['target'],
                unique_keys=[]
            )
            
            if progress_callback:
                await progress_callback("complete", "预览生成完成")
            
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
            
        finally:
            adapter.disconnect()
    
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
                    replication = config.get('defaults', {}).get('replication', 3)
                    
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
