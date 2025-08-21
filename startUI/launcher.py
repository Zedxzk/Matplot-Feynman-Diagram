import os
import subprocess
import sys
import locale
import shutil
import json
import time
import importlib.metadata
import re # 正则表达式模块，是标准库的一部分

def check_requirements_native():
    """
    使用纯标准库检查依赖包是否安装并满足版本要求。
    """
    # 同样，从 setup.py 复制需求列表
    requirements = [
        "matplotlib>=3.7.2",
        "mplhep>=0.3.59",
        "numpy>=1.23",
        "Pygments>=2.19",
        "PySide6>=6.9",
        "PySide6-Addons>=6.9",
        "PySide6-Essentials>=6.9",
        "scipy>=1.11.3",
    ]

    missing_or_wrong_version = []

    def version_to_tuple(v_str):
        """将 '3.7.2' 这样的版本字符串转换为可比较的元组 (3, 7, 2)"""
        try:
            # 移除可能存在的预发布标签等，只保留主版本号
            main_version = v_str.split('+')[0].split('-')[0]
            return tuple(map(int, main_version.split('.')))
        except ValueError:
            # 如果版本号格式复杂，返回一个最小的值以示无法比较
            return (0,)

    print("Checking required packages (using standard library)...")
    for req_str in requirements:
        # 使用正则表达式从 "package>=version" 中提取三部分
        match = re.match(r"([a-zA-Z0-9\-_]+)\s*(>=)\s*([0-9\.]+)", req_str)
        if not match:
            print(f"Warning: Could not parse requirement string '{req_str}'")
            continue

        name, operator, required_version_str = match.groups()

        try:
            installed_version_str = importlib.metadata.version(name)
            
            # 将版本号转换为元组进行比较
            installed_tuple = version_to_tuple(installed_version_str)
            required_tuple = version_to_tuple(required_version_str)

            # 执行版本比较
            if operator == '>=':
                if installed_tuple < required_tuple:
                    missing_or_wrong_version.append(
                        f"  - {name} (需要版本 {req_str}，但已安装版本是 {installed_version_str})"
                    )

        except importlib.metadata.PackageNotFoundError:
            missing_or_wrong_version.append(
                f"  - {name} (未安装，需要版本 {req_str})"
            )
        except Exception as e:
            missing_or_wrong_version.append(
                f"  - 检查 {name} 时出错: {e}"
            )

    if not missing_or_wrong_version:
        print("All requirements are satisfied.")
        return True
    else:
        print("\n--- 缺少或版本错误的依赖包 ---")
        print("目标 Python 环境缺少必要的依赖包或版本不兼容。")
        print("请运行以下命令来安装或更新它们:")
        
        packages_to_install = [req.split('>=')[0] for req in requirements]
        print(f"\n  pip install --upgrade {' '.join(packages_to_install)}\n")
        
        print("问题详情:")
        for problem in missing_or_wrong_version:
            print(problem)
        print("-----------------------------------")
        return False
    
def find_python_executable():
    """
    寻找可用的 Python 解释器，优先使用当前激活的环境。
    """
    # 1. 优先使用当前 Python 解释器（如果不是打包的 exe）
    if not getattr(sys, 'frozen', False):
        return sys.executable


    # 2. 检查是否在 conda 环境中
    conda_prefix = os.environ.get('CONDA_PREFIX')
    

    # --- 关键修改在这里 ---
    # 必须先判断 conda_prefix 是否存在，然后再使用它
    if conda_prefix and os.path.isdir(conda_prefix):
        print(f"Conda prefix found: {conda_prefix}")
        # 尝试使用 conda 环境中的 Python
        if sys.platform == 'win32':
            conda_python = os.path.join(conda_prefix, 'python.exe')
        else:
            conda_python = os.path.join(conda_prefix, 'bin', 'python')
        
        if os.path.isfile(conda_python):
            print(f"Conda python found: {conda_python}")
            return conda_python
    else:
        # 在EXE环境中，conda_prefix很可能是None，这是正常的
        print("Conda prefix not found in environment.")
    # --- 修改结束 ---

    # 3. 检查虚拟环境
    virtual_env = os.environ.get('VIRTUAL_ENV')
    if virtual_env and os.path.isdir(virtual_env):
        print(f"Virtual env found: {virtual_env}")
        if sys.platform == 'win32':
            venv_python = os.path.join(virtual_env, 'Scripts', 'python.exe')
        else:
            venv_python = os.path.join(virtual_env, 'bin', 'python')
        
        if os.path.isfile(venv_python):
            return venv_python

    # 4. 在 PATH 中寻找
    print("Searching for python in PATH...")
    for name in ["python", "python3"]:
        python_exe = shutil.which(name)
        if python_exe:
            print(f"Found python in PATH: {python_exe}")
            return python_exe
    
    return None

def get_pip_for_python(python_exe):
    """
    获取与指定 Python 解释器配套的 pip 路径。
    """
    try:
        # 使用 python -m pip 确保使用正确的 pip
        result = subprocess.run(
            [python_exe, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        if result.returncode == 0:
            return [python_exe, "-m", "pip"]
    except Exception:
        pass
    
    # 如果 python -m pip 不可用，尝试直接找 pip
    python_dir = os.path.dirname(python_exe)
    if sys.platform == 'win32':
        pip_paths = [
            os.path.join(python_dir, "Scripts", "pip.exe"),
            os.path.join(python_dir, "pip.exe")
        ]
    else:
        pip_paths = [
            os.path.join(python_dir, "pip"),
            os.path.join(python_dir, "pip3")
        ]
    
    for pip_path in pip_paths:
        if os.path.isfile(pip_path):
            return [pip_path]
    
    return None

def verify_python_pip_compatibility(python_exe, pip_cmd):
    """
    验证 Python 和 pip 是否来自同一个环境。
    """
    try:
        # 获取 Python 的 site-packages 路径
        python_result = subprocess.run(
            [python_exe, "-c", 
             "import site; import json; print(json.dumps(site.getsitepackages()))"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        if python_result.returncode != 0:
            return False
        
        python_site_packages = set(json.loads(python_result.stdout))
        
        # 获取 pip 的安装位置
        pip_result = subprocess.run(
            pip_cmd + ["show", "pip"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        if pip_result.returncode != 0:
            return False
        
        # 解析 pip show 输出，找到 Location
        pip_location = None
        for line in pip_result.stdout.split('\n'):
            if line.startswith('Location:'):
                pip_location = line.split(':', 1)[1].strip()
                break
        
        if not pip_location:
            return False
        
        # 检查 pip 的位置是否在 Python 的 site-packages 中
        return any(pip_location.startswith(sp) for sp in python_site_packages)
        
    except Exception:
        return False

def get_system_language():
    """
    获取系统的首选语言，兼容多种操作系统和语言格式。
    """
    try:
        lang_code = locale.getlocale()[0]
        if lang_code:
            return lang_code.split('_')[0].lower()
    except Exception:
        pass
    
    try:
        lang_name = locale.getlocale(locale.LC_CTYPE)[0]
        if lang_name and ('chinese' in lang_name.lower() or 'zh' in lang_name.lower()):
            return 'zh'
    except Exception:
        pass

    return 'en'

def run_command(command, timeout=30):
    """
    辅助函数，用于执行子进程命令。
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        stdout, stderr = process.communicate(timeout=timeout)
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
        return True, stdout, stderr
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        stderr_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
        return False, '', stderr_msg

def check_and_run_pyfeynplot():
    """
    检查并运行 pyfeynplot 的主函数。
    """
    lang = get_system_language()
    
    text = {
        'zh': {
            'checking_python': "正在寻找系统 Python 环境...",
            'err_no_python': "错误：在系统中未找到 Python 环境，请先安装 Python。",
            'python_ok': "找到 Python 环境:",
            'checking_pip': "正在检查 pip 工具...",
            'err_no_pip': "错误：pip 工具不可用，请确保 Python 环境完整。\n详细信息：",
            'pip_ok': "pip 工具可用:",
            'checking_compatibility': "正在验证 Python 和 pip 的兼容性...",
            'err_incompatible': "警告：Python 和 pip 可能来自不同环境，这可能导致安装问题。",
            'compatibility_ok': "Python 和 pip 环境匹配。",
            'checking_pyfeynplot': "正在检查 pyfeynplot 是否已安装...",
            'pyfeynplot_installed': "检测到 pyfeynplot 已安装。",
            'starting_gui': "正在启动 pyfeynplot...",
            'err_no_start': "错误：无法启动 pyfeynplot。请尝试在命令行手动运行。",
            'not_installed_prompt': "未检测到 pyfeynplot，是否现在从本地源码安装？(Y/N)",
            'installing': "正在安装 pyfeynplot...",
            'install_success': "安装成功！正在启动 pyfeynplot...",
            'install_failed': '错误：安装失败，请检查错误信息。\n详细信息：',
            'install_canceled': "已取消安装。",
            'changing_dir': "正在切换到脚本所在目录进行安装...",
            'press_any_key': "按任意键退出...",
            'env_info': "环境信息："
        },
        'en': {            
            'checking_python': "Checking for Python environment...",
            'err_no_python': "Error: Python not found. Please install Python first.",
            'python_ok': "Python environment found:",
            'checking_pip': "Checking for pip tool...",
            'err_no_pip': "Error: pip not available. Please ensure your Python installation is complete.\nDetails:",
            'pip_ok': "pip tool available:",
            'checking_compatibility': "Verifying Python and pip compatibility...",
            'err_incompatible': "Warning: Python and pip may be from different environments, which could cause installation issues.",
            'compatibility_ok': "Python and pip environments are compatible.",
            'checking_pyfeynplot': "Checking if pyfeynplot is installed...",
            'pyfeynplot_installed': "pyfeynplot is already installed.",
            'starting_gui': "Starting pyfeynplot...",
            'err_no_start': "Error: Could not start pyfeynplot. Try running it manually from command line.",
            'not_installed_prompt': "pyfeynplot not found. Do you want to install it from local source now? (Y/N)",
            'installing': "Installing pyfeynplot...",
            'install_success': "Installation successful! Starting pyfeynplot...",
            'install_failed': 'Error: Installation failed. Please check the error message.\nDetails:',
            'install_canceled': "Installation canceled.",
            'changing_dir': "Changing to script directory for installation...",
            'press_any_key': "Press any key to exit...",
            'env_info': "Environment info:"
        }
    }

    current_text = text.get(lang, text['en'])

    def pause_and_exit(message=""):
        if message:
            print(message)
        input(current_text['press_any_key'])
        sys.exit(1)

    # 1. 寻找 Python 解释器
    print(current_text['checking_python'])
    # 获取当前 Python 解释器路径
    # print(f"DEBUG: {sys.executable}")
    python_exe = find_python_executable()
    if not python_exe:
        pause_and_exit(current_text['err_no_python'])
    print(f"{current_text['python_ok']} {python_exe}")

    # 显示环境信息
    print(f"\n{current_text['env_info']}")
    if os.environ.get('CONDA_PREFIX'):
        print(f"  Conda 环境: {os.environ['CONDA_PREFIX']}")
    if os.environ.get('VIRTUAL_ENV'):
        print(f"  虚拟环境: {os.environ['VIRTUAL_ENV']}")
    print()
    # --- 调用新的原生检查函数 ---
    if not check_requirements_native():
        print("因缺少依赖包而中止。")
        return None
    # --- 结束调用 ---
    # 2. 检查 pip
    print(current_text['checking_pip'])
    pip_cmd = get_pip_for_python(python_exe)
    if not pip_cmd:
        pause_and_exit(current_text['err_no_pip'])
    
    # 验证 pip 是否可用
    success, _, stderr = run_command(pip_cmd + ["--version"])
    if not success:
        pause_and_exit(f"{current_text['err_no_pip']}\n{stderr}")
    
    print(f"{current_text['pip_ok']} {' '.join(pip_cmd)}")

    # 3. 验证 Python 和 pip 的兼容性
    print(current_text['checking_compatibility'])
    if verify_python_pip_compatibility(python_exe, pip_cmd):
        print(current_text['compatibility_ok'])
    else:
        print(current_text['err_incompatible'])
        # 继续执行，但给出警告

    # 4. 检查 pyfeynplot 是否已安装
    print(current_text['checking_pyfeynplot'])
    success, test, test2 = run_command(pip_cmd + ["show", "pyfeynplot"])
    print(f"DEBUG: pip show pyfeynplot output: {test}, error: {test2}")
    is_installed = success

    if not is_installed:
        install_choice = input(f"{current_text['not_installed_prompt']} ").strip().lower()
        if install_choice == 'y':
            print(current_text['installing'])
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            try:
                print(f"{current_text['changing_dir']} -> {script_dir}")
                os.chdir(script_dir)
            except Exception as e:
                pause_and_exit(f"Error changing directory: {e}")

            success, _, stderr = run_command(pip_cmd + ["install", "-e", "."], timeout=180)
            if not success:
                pause_and_exit(f"{current_text['install_failed']}\n{stderr}")
            print(current_text['install_success'])
        else:
            pause_and_exit(current_text['install_canceled'])
    else:
        print(current_text['pyfeynplot_installed'])

    # 5. 启动程序
    print(current_text['starting_gui'])
    try:
        project_root = ''
        
        # --- 这是实现您想法的关键修改 ---
        # 判断当前是在打包的EXE环境中，还是在开发的.py脚本环境中
        if getattr(sys, 'frozen', False):
            # 如果是打包后的EXE文件，project_root就是EXE所在的目录
            # sys.executable 在这种情况下指向 Feynplot.exe
            print("Running in a bundled EXE.")
            project_root = os.path.dirname(sys.executable)
        else:
            # 如果是直接运行.py脚本，使用我们之前的逻辑
            # sys.argv[0] 在这种情况下指向 launcher.py
            print("Running as a .py script.")
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            project_root = os.path.dirname(script_dir)
        
        # --- 修改结束 ---

        command_to_run = [python_exe, "-m", "feynplot_gui"]
        
        print(f"--- Starting Process ---")
        print(f"Executable: {command_to_run[0]}")
        print(f"Command: {' '.join(command_to_run)}")
        print(f"Project Root (CWD): {project_root}")
        print("------------------------")
        
        # 启动子进程，并明确指定正确的工作目录
        subprocess.Popen(
            command_to_run,
            cwd=project_root
        )

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        pause_and_exit(f"{current_text['err_no_start']}\n{e}")


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    
    check_and_run_pyfeynplot()
    time.sleep(5)  # 确保子进程有时间启动