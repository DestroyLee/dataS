"""
日志配置模块
提供统一的日志记录功能，替代print语句
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "doris_sync",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回logger实例
    
    Args:
        name: logger名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则只输出到控制台
        format_string: 自定义日志格式
        
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 默认日志格式
    if format_string is None:
        format_string = (
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )
    
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 创建全局logger实例
logger = setup_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取logger实例
    
    Args:
        name: logger名称，如果为None则返回全局logger
        
    Returns:
        logger实例
    """
    if name is None:
        return logger
    return setup_logger(name)
