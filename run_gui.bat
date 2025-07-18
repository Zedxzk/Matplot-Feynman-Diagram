@echo off
chcp 65001 >nul  

:: 切换到当前脚本所在目录
cd /d %~dp0
echo 当前工作目录：%cd%

:: 激活虚拟环境（如果需要，替换为你的环境路径）
:: call D:\Software\MiniConda\Scripts\activate.bat D:\Software\MiniConda\envs\your_env_name

:: 检查 Python 是否可用
echo 正在检查 Python 环境...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误：未找到 Python 环境，请先安装 Python 并配置环境变量。
    pause
    exit /b 1
)

:: 检查 pip 是否可用
echo 正在检查 pip 工具...
pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误：未找到 pip 工具，请先安装 pip（通常随 Python 自动安装）。
    pause
    exit /b 1
)

:: 检查 pyfeynplot 是否已安装（修正此处：使用半角空格）
echo 正在检查 pyfeynplot 是否安装...
python -m pip show pyfeynplot >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo 检测到 pyfeynplot 已安装（版本信息见下方）：
    python -m pip show pyfeynplot
    echo 正在启动 pyfeynplot...
    feynplot-gui
    exit /b 0
)

:: 未安装时提示安装
echo 未检测到 pyfeynplot，是否现在安装？(Y/N)
set /p install_choice=
if /i "!install_choice!"=="Y" (
    echo 正在安装 pyfeynplot...
    pip install -e .
    if %ERRORLEVEL% equ 0 (
        echo 安装成功！正在启动 pyfeynplot...
        python -m pyfeynplot
    ) else (
        echo 错误：安装失败，请手动执行 "pip install -e ." 重试。
    )
) else (
    echo 已取消安装。
)

pause