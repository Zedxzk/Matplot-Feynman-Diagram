@echo off
setlocal

:: 切换到当前脚本所在目录（确保路径正确）
cd /d "%~dp0"

echo [Matplot-Feynman-Diagram Launcher]
echo Checking Python environment...

:: 1. 检查是否有 python 命令
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not found. Please install Python 3.10+ and add it to PATH.
    echo 错误：未找到 Python。请安装 Python 3.10+ 并勾选 "Add to PATH"。
    pause
    exit /b 1
)

:: 2. 尝试启动启动器脚本 (它会负责检查依赖和启动 GUI)
:: 使用 py -3 如果可用，否则使用 python
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py -3 startUI/launcher.py
) else (
    python startUI/launcher.py
)

:: 如果启动脚本返回错误 (例如崩溃)，暂停显示错误信息
if %ERRORLEVEL% neq 0 (
    echo.
    echo The application exited with an error.
    pause
)
