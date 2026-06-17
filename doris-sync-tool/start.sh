#!/bin/bash

# Doris 同步工具 - 快速启动脚本 (前后端同时启动)

echo "======================================"
echo "Doris Sync Tool - 快速启动"
echo "======================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ 错误：未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo "✅ Python 版本：$($PYTHON_CMD --version)"
echo ""

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

echo "✅ Node.js 版本：$(node --version)"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 安装后端依赖
echo "📦 正在安装后端依赖..."
$PYTHON_CMD -m pip install -r backend/requirements.txt --quiet
echo "✅ 后端依赖安装完成"
echo ""

# 安装前端依赖
echo "📦 正在安装前端依赖..."
cd frontend
npm install --silent
cd ..
echo "✅ 前端依赖安装完成"
echo ""

# 创建必要的数据目录
mkdir -p backend/data/configs
mkdir -p output

echo "======================================"
echo "🚀 启动服务..."
echo "======================================"
echo ""
echo "后端 API: http://localhost:8000"
echo "API 文档：http://localhost:8000/docs"
echo "前端界面：http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 启动后端
echo "▶️  启动后端服务..."
$PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "▶️  启动前端服务..."
cd frontend
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
cd ..

# 等待进程结束
wait $BACKEND_PID $FRONTEND_PID
