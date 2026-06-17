# dataS - Doris 数据同步工具

## 项目简介

**dataS** (Doris Sync Tool) 是一个功能强大的数据同步自动化工具，专为 MySQL 到 Apache Doris 的数据迁移和同步场景设计。它提供命令行工具和 Web 界面两种方式，帮助用户快速完成数据同步的准备工作。

### 核心功能

- ✅ **自动采集元数据**：从 MySQL 自动采集表结构、数据类型、行数统计等信息
- ✅ **智能建表 SQL 生成**：根据源表结构自动生成 Doris 建表 DDL，支持 Unique Key 模型
- ✅ **分桶策略优化**：基于数据量智能计算最优分桶数，避免数据倾斜
- ✅ **DataX 配置生成**：自动生成 DataX 数据同步任务配置文件
- ✅ **Web 管理界面**：提供可视化的配置管理和任务预览功能
- ✅ **特殊类型映射**：完美处理 unsigned、enum、blob 等 MySQL 特殊类型
- ✅ **安全配置管理**：支持环境变量管理敏感信息，配置脱敏日志

### 技术栈

**后端**
- Python 3.8+
- FastAPI (Web API)
- Jinja2 (模板引擎)
- PyYAML (配置解析)
- Click (命令行工具)

**前端**
- Vue 3 + Vite
- Element Plus (UI 组件库)
- Monaco Editor (代码编辑器)
- Axios (HTTP 客户端)
- Pinia (状态管理)

## 快速开始

### 方式一：命令行工具

#### 1. 安装依赖

```bash
cd doris-sync-tool
pip install -r requirements.txt
```

#### 2. 配置同步任务

复制示例配置文件并修改：

```bash
cp config/sync_task.yaml.example config/sync_task.yaml
```

编辑 `config/sync_task.yaml`，填写你的数据库信息和需要同步的表。

#### 3. 运行工具

```bash
python main.py --config config/sync_task.yaml --output ./output
```

#### 4. 查看输出

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

### 方式二：Web 界面（推荐）

#### 1. 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

#### 2. 一键启动

```bash
cd doris-sync-tool
chmod +x start.sh
./start.sh
```

启动后访问：
- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

#### 3. 使用步骤

1. **创建配置**：在 Web 界面填写 MySQL 和 Doris 连接信息
2. **选择表**：从 MySQL 数据库中选择需要同步的表
3. **预览配置**：查看生成的 DDL 和 DataX 配置
4. **下载文件**：下载生成的 SQL 和 JSON 文件
5. **执行同步**：在 Doris 中执行 DDL，使用 DataX 运行同步任务

## 配置说明

### 核心配置项

```yaml
# 源数据库配置 (MySQL)
source:
  type: mysql
  host: 192.168.1.100          # MySQL 地址
  port: 3306
  user: root                   # 用户名
  password: your_password      # 密码
  database: order_db           # 源数据库名

# 目标数据库配置 (Doris)
target:
  type: doris
  fe_host: 192.168.1.200       # Doris FE 地址
  http_port: 8030
  query_port: 9030
  user: root                   # Doris 用户名
  password: your_password      # Doris 密码
  database: ods_order_db       # 目标数据库名

# 默认配置
defaults:
  bucket_strategy: auto        # 自动分桶策略
  replication: 3               # 副本数

# 需要同步的表配置
tables:
  - table_name: t_order_info
    unique_keys: ["order_id", "update_time"]  # Unique Key 字段
    distribution_columns: ["order_id"]        # 可选：自定义分布列
    
  - table_name: t_order_detail
    unique_keys: ["order_id", "sku_id"]
    
  - table_name: t_user_profile
    unique_keys: ["user_id"]
```

### Unique Key 配置说明

- **配置 `unique_keys`**：生成 UNIQUE KEY 模型的 Doris 表，支持数据更新和去重
- **不配置或为空**：生成普通 Duplicate Key 模型表

### 分桶策略

工具采用智能分桶算法，根据数据量自动计算最优分桶数：

| 数据量 | 分桶数 |
|--------|--------|
| 0 - 100 万 | 1 |
| 100 万 - 500 万 | 8 |
| 500 万 - 2000 万 | 16 |
| 2000 万 - 1 亿 | 32 |
| > 1 亿 | 64 (上限) |

## 架构设计

```
doris-sync-tool/
├── src/                      # 核心源码
│   ├── adapters/             # 数据源适配器 (支持扩展其他数据库)
│   │   ├── base.py           # 适配器基类
│   │   └── mysql.py          # MySQL 适配器实现
│   ├── strategies/           # 分桶策略 (支持自定义策略)
│   │   └── base.py           # 策略基类
│   ├── generators/           # DDL 和 DataX 配置生成器
│   │   └── __init__.py       # 生成器实现
│   ├── core/                 # 核心流程引擎和配置加载
│   │   ├── loader.py         # 配置加载器
│   │   └── engine.py         # 同步引擎
│   └── utils/                # 工具函数
│       ├── logger.py         # 日志配置
│       └── security.py       # 安全工具 (配置脱敏)
├── backend/                  # Web 后端 (FastAPI)
│   ├── api/                  # API 路由
│   │   ├── config.py         # 配置管理 API
│   │   ├── preview.py        # 预览 API
│   │   └── tasks.py          # 任务管理 API
│   ├── models/               # 数据模型
│   ├── services/             # 业务服务
│   └── main.py               # FastAPI 入口
├── frontend/                 # Web 前端 (Vue 3)
│   ├── src/
│   │   ├── api/              # API 调用封装
│   │   ├── views/            # 页面组件
│   │   ├── router.js         # 路由配置
│   │   └── App.vue           # 根组件
│   └── package.json
├── config/                   # 配置文件
│   ├── sync_task.yaml        # 用户配置
│   ├── sync_task.yaml.example # 配置示例
│   └── templates/            # Jinja2 模板
├── tests/                    # 测试文件
├── main.py                   # 命令行入口
├── start.sh                  # 快速启动脚本
└── requirements.txt          # Python 依赖
```

## 下一步操作

1. **执行 DDL**: 在 Doris 中运行 `output/ddl/*.sql` 创建 ODS 层表
2. **运行 DataX**: 使用生成的 JSON 配置执行数据同步
   ```bash
   python $DATAX_HOME/bin/datax.py output/datax/t_order_info.json
   ```
3. **配置调度** (可选): 将 DataX 任务配置到海豚调度平台

## 扩展开发

### 添加新的数据源适配器

继承 `src/adapters/base.py` 中的 `SourceAdapter` 抽象类：

```python
from src.adapters.base import SourceAdapter

class PostgreSQLAdapter(SourceAdapter):
    def connect(self):
        # 实现 PostgreSQL 连接逻辑
        pass
    
    def fetch_table_metadata(self, table_name):
        # 实现元数据采集逻辑
        pass
```

### 自定义分桶策略

继承 `src/strategies/base.py` 中的 `DistributionStrategy` 抽象类：

```python
from src.strategies.base import DistributionStrategy

class CustomBucketStrategy(DistributionStrategy):
    def calculate_buckets(self, row_count, column_type):
        # 实现自定义分桶算法
        pass
```

## 常见问题

### Q: 如何处理 MySQL 的特殊数据类型？

A: 工具已内置常见特殊类型的映射规则：
- `UNSIGNED` 整数 → Doris 对应的大一级整数类型
- `ENUM` → VARCHAR
- `BLOB/TEXT` → VARCHAR 或 STRING
- `DATETIME/TIMESTAMP` → DATETIME

### Q: 分桶数不合适怎么办？

A: 可以在配置中手动指定 `distribution_columns` 和分桶数，或在生成后手动调整 SQL。

### Q: 如何保证数据安全？

A: 
- 密码等敏感信息建议使用环境变量
- 日志输出会自动脱敏配置信息
- 生产环境请限制 CORS 允许的来源

### Q: 支持增量同步吗？

A: 当前版本主要支持全量同步的准备工作。增量同步需要配合 DataX 的增量读取插件和 Doris 的 Unique Key 模型实现。

## 测试报告

详细的测试结果请参考 [tests/test_results.md](doris-sync-tool/tests/test_results.md)

## License

MIT