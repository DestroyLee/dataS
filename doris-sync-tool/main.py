import click
import os
import logging
from src.utils.logger import setup_logger
from src.core.loader import ConfigLoader
from src.core.engine import SyncEngine

# 初始化日志
logger = setup_logger()

@click.command()
@click.option('--config', '-c', required=True, help='YAML 配置文件路径')
@click.option('--output', '-o', default='./output', help='输出目录路径')
@click.option('--log-level', '-l', default='INFO', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='日志级别')
@click.option('--log-file', '-f', default=None, help='日志文件路径')
def main(config, output, log_level, log_file):
    """Doris 同步自动化工具 - 优化版本
    
    从 MySQL 自动采集元数据，生成 Doris 建表 SQL 和 DataX 同步配置
    
    支持：
    - 完善的错误处理和日志记录
    - 环境变量管理敏感配置
    - 特殊类型映射（unsigned, enum, blob 等）
    """
    
    # 重新配置日志级别
    global logger
    logger = setup_logger(log_level=log_level, log_file=log_file)
    
    try:
        # 加载并验证配置
        logger.info(f"正在加载配置文件：{config}")
        config_data = ConfigLoader.load(config)
        ConfigLoader.validate(config_data)
        
        # 打印脱敏后的配置
        ConfigLoader.log_config(config_data)
        
        # 获取模板目录
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'templates')
        if not os.path.exists(template_dir):
            # 尝试从当前工作目录查找
            template_dir = os.path.join(os.getcwd(), 'config', 'templates')
        
        if not os.path.exists(template_dir):
            logger.error(f"❌ 模板目录不存在：{template_dir}")
            return
        
        # 执行引擎
        engine = SyncEngine(config_data, template_dir)
        engine.execute(output)
        
    except FileNotFoundError as e:
        logger.error(f"文件未找到：{e}")
        raise click.Abort()
    except ValueError as e:
        logger.error(f"配置错误：{e}")
        raise click.Abort()
    except Exception as e:
        logger.error(f"执行失败：{e}", exc_info=True)
        raise click.Abort()

if __name__ == '__main__':
    main()
