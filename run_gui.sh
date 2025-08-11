#!/usr/bin/env bash
# -------------------------------------------------
# run_pyfeynplot.sh
# -------------------------------------------------

# 切换到脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || { echo "无法进入脚本目录"; exit 1; }

# -------------------------------------------------
# 语言本地化函数（只取前 2 字符）
# -------------------------------------------------
get_localized_string() {
    local key="$1"
    local lang="${LANG:0:2}"   # 只截取前 2 字符，如 zh / en / ja ...
    case "$lang" in
        zh)
            case "$key" in
                cwd)    echo "当前工作目录：$SCRIPT_DIR";;
                check_py) echo "正在检查 Python 环境...";;
                no_py)  echo "错误：未找到 Python 环境，请先安装 Python 并配置环境变量（推荐 Python 3.7+）。";;
                check_pip) echo "正在检查 pip 工具...";;
                no_pip) echo "错误：未找到 pip 工具，请先安装 pip（通常随 Python 自动安装）。";;
                check_pkg) echo "正在检查 pyfeynplot 是否安装...";;
                found)  echo "检测到 pyfeynplot 已安装（版本信息见下方）：";;
                start)  echo "正在启动 pyfeynplot...";;
                ask)    echo "未检测到 pyfeynplot，是否现在安装？(Y/N)";;
                input)  echo "输入 Y 继续安装，其他键取消: ";;
                ok)     echo "安装成功！正在启动 pyfeynplot...";;
                fail)   echo "错误：安装失败，请手动执行以下命令重试：";;
                cancel) echo "已取消安装。";;
                bye)    echo "按任意键退出...";;
                *)      echo "$key";;  # fallback
            esac
            ;;
        *)
            # 默认英文
            case "$key" in
                cwd)    echo "Current working directory: $SCRIPT_DIR";;
                check_py) echo "Checking Python environment...";;
                no_py)  echo "Error: Python not found. Please install Python (3.7+ recommended) and ensure it is on PATH.";;
                check_pip) echo "Checking pip tool...";;
                no_pip) echo "Error: pip not found. It usually comes with Python.";;
                check_pkg) echo "Checking if pyfeynplot is installed...";;
                found)  echo "pyfeynplot is detected as installed (version info below):";;
                start)  echo "Starting pyfeynplot...";;
                ask)    echo "pyfeynplot not detected. Install now? (Y/N)";;
                input)  echo "Enter Y to continue installation, any other key to cancel: ";;
                ok)     echo "Installation successful! Starting pyfeynplot...";;
                fail)   echo "Error: Installation failed. Please retry manually with:";;
                cancel) echo "Installation cancelled.";;
                bye)    echo "Press any key to exit...";;
                *)      echo "$key";;  # fallback
            esac
            ;;
    esac
}

# -------------------------------------------------
# 主流程
# -------------------------------------------------
echo "$(get_localized_string cwd)"
echo "LANG:${LANG:0:2}"
# 检查 Python
echo "$(get_localized_string check_py)"
if ! command -v python &>/dev/null; then
    echo "$(get_localized_string no_py)"
    read -rn1
    exit 1
fi

# 检查 pip
echo "$(get_localized_string check_pip)"
if ! python -m pip --version &>/dev/null; then
    echo "$(get_localized_string no_pip)"
    read -rn1
    exit 1
fi

# 检查是否已安装 pyfeynplot
echo "$(get_localized_string check_pkg)"
if python -m pip show pyfeynplot &>/dev/null; then
    echo "$(get_localized_string found)"
    python -m pip show pyfeynplot
    echo "$(get_localized_string start)"
    feynplot-gui      # 若启动命令不同，请替换
    exit 0
fi

# 未安装则询问安装
echo "$(get_localized_string ask)"
read -p "$(get_localized_string input)" -n1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "$(get_localized_string ok)"
    if python -m pip install -e .; then
        feynplot-gui  # 若启动命令不同，请替换
    else
        echo "$(get_localized_string fail)"
        echo "  python -m pip install -e ."
    fi
else
    echo "$(get_localized_string cancel)"
fi

read -rn1 -p "$(get_localized_string bye)"
echo