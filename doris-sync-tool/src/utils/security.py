"""
配置安全模块
支持从环境变量加载敏感配置，避免硬编码密码
"""

import os
from typing import Dict, Any, Optional


class ConfigSecurity:
    """配置安全管理器"""
    
    # 敏感配置键名映射（配置文件键名 -> 环境变量名前缀）
    SENSITIVE_KEYS = {
        'password': 'DB_PASSWORD',
        'user': 'DB_USER',
        'host': 'DB_HOST',
    }
    
    @classmethod
    def load_from_env(
        cls, 
        config: Dict[str, Any], 
        prefix: str = "DORIS_SYNC",
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        从环境变量加载敏感配置
        
        Args:
            config: 原始配置字典
            prefix: 环境变量前缀，默认 DORIS_SYNC
                     例如：DORIS_SYNC_SOURCE_PASSWORD
            strict: 严格模式，如果环境变量不存在是否抛出异常
            
        Returns:
            合并后的配置字典
            
        Example:
            # 配置文件中使用 ${PASSWORD} 或直接留空
            # 设置环境变量: export DORIS_SYNC_SOURCE_PASSWORD=your_password
        """
        import copy
        config = copy.deepcopy(config)
        
        # 处理 source 配置
        if 'source' in config:
            config['source'] = cls._load_section_env(
                config['source'], 
                'SOURCE',
                prefix,
                strict
            )
        
        # 处理 target 配置
        if 'target' in config:
            config['target'] = cls._load_section_env(
                config['target'],
                'TARGET', 
                prefix,
                strict
            )
        
        return config
    
    @classmethod
    def _load_section_env(
        cls,
        section: Dict[str, Any],
        section_name: str,
        prefix: str,
        strict: bool
    ) -> Dict[str, Any]:
        """处理单个配置段的环境变量加载"""
        for key in cls.SENSITIVE_KEYS.keys():
            if key in section:
                # 如果配置值为空或特定占位符，尝试从环境变量加载
                current_value = section[key]
                if current_value in ('', None, 'your_password', '${PASSWORD}'):
                    env_var_name = f"{prefix}_{section_name}_{cls.SENSITIVE_KEYS[key].upper()}"
                    env_value = os.getenv(env_var_name)
                    
                    if env_value is not None:
                        section[key] = env_value
                    elif strict and key == 'password':
                        raise ValueError(
                            f"敏感配置 '{key}' 未设置，且环境变量 {env_var_name} 不存在"
                        )
        
        return section
    
    @classmethod
    def mask_sensitive_info(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        脱敏显示配置信息（用于日志打印）
        
        Args:
            config: 配置字典
            
        Returns:
            脱敏后的配置字典
        """
        import copy
        masked = copy.deepcopy(config)
        
        for section in ['source', 'target']:
            if section in masked:
                if 'password' in masked[section]:
                    pwd = masked[section]['password']
                    if pwd and len(pwd) > 2:
                        masked[section]['password'] = pwd[:2] + '*' * (len(pwd) - 2)
                    else:
                        masked[section]['password'] = '***'
        
        return masked
    
    @classmethod
    def validate_security(cls, config: Dict[str, Any]) -> list:
        """
        检查配置安全性问题
        
        Args:
            config: 配置字典
            
        Returns:
            安全问题列表
        """
        warnings = []
        
        for section in ['source', 'target']:
            if section in config:
                password = config[section].get('password', '')
                
                # 检查弱密码
                if password in ('your_password', '123456', 'password', ''):
                    warnings.append(
                        f"⚠️  {section} 配置使用弱密码或空密码，建议使用环境变量"
                    )
                
                # 检查是否硬编码
                if password and password not in ('your_password', '', None):
                    if len(password) < 8:
                        warnings.append(
                            f"⚠️  {section} 密码长度小于 8 位，存在安全风险"
                        )
        
        return warnings
