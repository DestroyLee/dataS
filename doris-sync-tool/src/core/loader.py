import yaml
import logging
from typing import Dict, Any
from src.utils.security import ConfigSecurity

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置文件加载器"""
    
    @staticmethod
    def load(config_path: str) -> dict:
        """加载 YAML 配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 从环境变量加载敏感配置
            config = ConfigSecurity.load_from_env(config, strict=False)
            
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {config_path}: {e}")
    
    @staticmethod
    def validate(config: dict) -> bool:
        """验证配置完整性"""
        required_keys = ['source', 'target', 'tables']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"缺少必需配置项：{key}")
        
        # 验证 source 配置
        source_required = ['host', 'user', 'password', 'database']
        for key in source_required:
            if key not in config['source']:
                raise ValueError(f"source 配置缺少：{key}")
        
        # 验证 target 配置
        target_required = ['fe_host', 'user', 'password', 'database']
        for key in target_required:
            if key not in config['target']:
                raise ValueError(f"target 配置缺少：{key}")
        
        # 检查安全性警告
        warnings = ConfigSecurity.validate_security(config)
        for warning in warnings:
            logger.warning(warning)
        
        return True
    
    @staticmethod
    def log_config(config: dict) -> None:
        """打印脱敏后的配置信息"""
        masked_config = ConfigSecurity.mask_sensitive_info(config)
        logger.info("已加载配置（敏感信息已脱敏）:")
        logger.info(f"  Source: {masked_config.get('source', {})}")
        logger.info(f"  Target: {masked_config.get('target', {})}")
        logger.info(f"  Tables: {[t.get('table_name') for t in config.get('tables', [])]}")
