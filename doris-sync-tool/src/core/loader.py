import yaml

class ConfigLoader:
    """配置文件加载器"""
    
    @staticmethod
    def load(config_path: str) -> dict:
        """加载YAML配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def validate(config: dict) -> bool:
        """验证配置完整性"""
        required_keys = ['source', 'target', 'tables']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"缺少必需配置项：{key}")
        
        # 验证source配置
        source_required = ['host', 'user', 'password', 'database']
        for key in source_required:
            if key not in config['source']:
                raise ValueError(f"source配置缺少：{key}")
        
        # 验证target配置
        target_required = ['fe_host', 'user', 'password', 'database']
        for key in target_required:
            if key not in config['target']:
                raise ValueError(f"target配置缺少：{key}")
        
        return True
