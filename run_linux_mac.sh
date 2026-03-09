#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "[Matplot-Feynman-Diagram Launcher]"

# 1. 检查 python3
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python 3 is not found."
    echo "错误：未找到 Python 3。"
    read -p "Press Enter to exit..."
    exit 1
fi

# 2. 运行启动脚本
echo "Launching with $PYTHON_CMD..."
"$PYTHON_CMD" startUI/launcher.py

# 3. 捕获退出状态
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "The application exited with error code $EXIT_CODE."
    read -p "Press Enter to exit..."
fi
