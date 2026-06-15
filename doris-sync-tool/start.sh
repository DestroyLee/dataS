#!/bin/bash

# Doris 同步工具 - 快速开始脚本

echo "======================================"
echo "Doris 同步自动化工具 - 快速开始"
echo "======================================"
echo ""

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误：未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

echo "✅ Python 版本：$(python --version)"
echo ""

# 安装依赖
echo "📦 正在安装依赖..."
pip install -r requirements.txt --quiet
echo "✅ 依赖安装完成"
echo ""

# 显示项目结构
echo "📁 项目结构:"
echo "doris-sync-tool/"
echo "├── config/"
echo "│   ├── templates/          # Jinja2 模板目录"
echo "│   ├── sync_task.yaml      # 你的配置文件（需编辑）"
echo "│   └── sync_task.yaml.example  # 配置示例"
echo "├── src/"
echo "│   ├── adapters/           # 数据源适配器"
echo "│   ├── strategies/         # 分桶策略"
echo "│   ├── generators/         # DDL/DataX生成器"
echo "│   └── core/               # 核心引擎"
echo "├── main.py                 # 入口脚本"
echo "└── tests/                  # 测试文件"
echo ""

# 提示用户编辑配置
echo "⚠️  下一步操作:"
echo ""
echo "1. 编辑配置文件:"
echo "   vim config/sync_task.yaml"
echo ""
echo "   需要修改的内容:"
echo "   - source.host: MySQL 地址"
echo "   - source.user/password: MySQL 认证信息"
echo "   - source.database: 源数据库名"
echo "   - target.fe_host: Doris FE 地址"
echo "   - target.user/password: Doris 认证信息"
echo "   - target.database: 目标数据库名"
echo "   - tables: 需要同步的表列表和 Unique Key 配置"
echo ""
echo "2. 运行工具:"
echo "   python main.py --config config/sync_task.yaml --output ./output"
echo ""
echo "3. 查看生成的文件:"
echo "   ls -la output/ddl/      # Doris 建表 SQL"
echo "   ls -la output/datax/    # DataX 任务配置"
echo ""
echo "4. 在 Doris 中执行 DDL:"
echo "   mysql -h <doris_fe_host> -P 9030 -u root -p < output/ddl/t_order_info.sql"
echo ""
echo "5. 运行 DataX 同步任务:"
echo "   python \$DATAX_HOME/bin/datax.py output/datax/t_order_info.json"
echo ""
echo "======================================"
echo "详细说明请查看 README.md"
echo "======================================"
