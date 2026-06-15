from abc import ABC, abstractmethod
from src.adapters.base import TableMeta

class DistributionStrategy(ABC):
    """分桶策略抽象基类"""
    
    @abstractmethod
    def get_bucket_num(self, row_count: int) -> int:
        """根据行数计算分桶数"""
        pass
    
    @abstractmethod
    def get_distribution_columns(self, table_meta: TableMeta, config: dict) -> list:
        """获取分布列"""
        pass

class AutoBucketStrategy(DistributionStrategy):
    """自动分桶策略：根据数据量智能计算"""
    
    # 每个分桶理想行数 (100万行)
    TARGET_ROWS_PER_BUCKET = 1000000
    MIN_BUCKETS = 1
    MAX_BUCKETS = 64
    
    def get_bucket_num(self, row_count: int) -> int:
        if row_count == 0:
            return self.MIN_BUCKETS
        
        calculated = row_count // self.TARGET_ROWS_PER_BUCKET
        bucket_num = max(self.MIN_BUCKETS, min(calculated, self.MAX_BUCKETS))
        
        # 向上取整到2的幂次，便于均衡
        if bucket_num > 0:
            bucket_num = 1 << (bucket_num - 1).bit_length()
        
        return max(self.MIN_BUCKETS, min(bucket_num, self.MAX_BUCKETS))
    
    def get_distribution_columns(self, table_meta: TableMeta, config: dict) -> list:
        # 优先使用配置中的distribution_columns
        if 'distribution_columns' in config and config['distribution_columns']:
            return config['distribution_columns']
        
        # 否则使用第一个字段作为分布列
        if table_meta.columns:
            return [table_meta.columns[0].name]
        
        return []
