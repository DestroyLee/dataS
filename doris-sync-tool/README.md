# Doris 同步自动化工具 (MVP)

## 项目简介

自动化完成从 MySQL 到 Doris 的数据同步准备工作：
- ✅ 自动采集 MySQL 表结构和数据量
- ✅ 智能生成分桶策略的 Doris 建表 SQL (支持 Unique Key)
- ✅ 自动生成 DataX 同步任务配置 JSON
- ⏳ 海豚调度集成 (后续版本)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置同步任务

复制示例配置文件并修改：

```bash
cp config/sync_task.yaml.example config/sync_task.yaml
```

编辑 `config/sync_task.yaml`，填写你的数据库信息和需要同步的表。

### 3. 运行工具

```bash
python main.py --config config/sync_task.yaml --output ./output
```

### 4. 查看输出

生成的文件结构：
```
output/
├── ddl/                    # Doris 建表 SQL
│   ├── t_order_info.sql
│   └── t_order_detail.sql
└── datax/                  # DataX 任务配置
    ├── t_order_info.json
    └── t_order_detail.json
```

## 配置说明

### 核心配置项

```yaml
source:          # 源 MySQL 数据库
  host: ...
  port: 3306
  user: ...
  password: ...
  database: ...

target:          # 目标 Doris 数据库
  fe_host: ...
  query_port: 9030
  user: ...
  password: ...
  database: ...

tables:          # 表配置列表
  - table_name: your_table
    unique_keys: ["id", "update_time"]  # Unique Key 字段
```

### Unique Key 配置

- 配置 `unique_keys`：生成 UNIQUE KEY 模型的 Doris 表
- 不配置或为空：生成普通 Duplicate Key 模型表

## 架构设计

```
src/
├── adapters/      # 数据源适配器 (支持扩展其他数据库)
├── strategies/    # 分桶策略 (支持自定义策略)
├── generators/    # DDL 和 DataX 配置生成器
└── core/          # 核心流程引擎和配置加载
```

## 下一步操作

1. **执行 DDL**: 在 Doris 中运行 `output/ddl/*.sql` 创建 ODS 层表
2. **运行 DataX**: 使用生成的 JSON 配置执行数据同步
   ```bash
   python datax.py output/datax/t_order_info.json
   ```
3. **配置调度** (可选): 将 DataX 任务手动配置到海豚调度平台

## 扩展开发

### 添加新的数据源适配器

继承 `src/adapters/base.py` 中的 `SourceAdapter` 抽象类

### 自定义分桶策略

继承 `src/strategies/base.py` 中的 `DistributionStrategy` 抽象类

## License

MIT
