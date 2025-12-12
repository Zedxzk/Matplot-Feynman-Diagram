#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
wrap_qt_strings.py

一个用于递归查找 .py 文件并自动为 Qt 控件中
未翻译的字符串添加 self.tr() 包裹的脚本。

用法:
    python wrap_qt_strings.py /path/to/your/project

警告：
    此脚本会直接修改您的 .py 文件。
    在运行前，请务必备份您的项目或使用版本控制 (如 Git)。
"""

import re
import sys
from pathlib import Path
from typing import List, Set

# 1. 简单单参数控件/方法
#    匹配如: QLabel("Text")
TARGETS_SIMPLE: List[str] = [
    'QLabel',
    'QPushButton',
    'QCheckBox',
    'QRadioButton',
    'QAction',
    'QGroupBox',
    'setWindowTitle',
    'setPlaceholderText',
    'setText',
    'addItem',
    'addTab',
    'setToolTip',
    'setStatusTip',
    'setWhatsThis',
]

# 2. QMessageBox (特殊处理，有两个字符串)
#    匹配如: QMessageBox.information(self, "Title", "Message")
TARGETS_MSGBOX: List[str] = [
    'information',
    'warning',
    'critical',
    'question',
]

def process_file(file_path: Path) -> bool:
    """
    处理单个 .py 文件，查找并替换未包裹的字符串。
    
    返回:
        bool: 如果文件被修改则返回 True，否则返回 False。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"  - 错误: 无法读取 {file_path}: {e}")
        return False

    content = original_content
    
    # --- 第 1 步: 处理简单的单参数目标 ---
    
    # 构建正则表达式:
    # (\b(QLabel|QPushButton|...)\s*\()  -> 匹配 'QLabel(' (Group 1 和 2)
    # (\s*(".*?"|'.*?')\s*)             -> 匹配字符串参数 '  "Text"  ' (Group 3)
    # \s*\)                               -> 匹配结束的 ')'
    
    # 我们只匹配字面字符串 ("..." or '...')
    # 这可以安全地跳过变量 (QLabel(var)) 和
    # 已经包裹的字符串 (QLabel(self.tr("...")))
    
    pattern_simple_str = r'(\b(' + r'|'.join(TARGETS_SIMPLE) + r')\s*\()(\s*(".*?"|\'.*?\')\s*)\)'
    
    # 替换函数：
    # m.group(1) = 'QLabel('
    # m.group(3) = '  "Text"  '
    # 替换为: 'QLabel(self.tr(  "Text"  ))'
    repl_simple = lambda m: f'{m.group(1)}self.tr({m.group(3).strip()}))'
    
    content = re.sub(pattern_simple_str, repl_simple, content)

    # --- 第 2 步: 处理 QMessageBox ---
    
    # 构建正则表达式:
    # (\b(QMessageBox\.(information|...))\s*\([^,]+,) -> 匹配 'QMessageBox.information(self,' (Group 1)
    # (\s*(".*?"|\'.*?\')\s*,)                         -> 匹配标题 '  "Title"  ,' (Group 4)
    # (\s*(".*?"|\'.*?\')\s*)                          -> 匹配消息 '  "Message"  ' (Group 6)
    # ((?:,.*)?)\)                                     -> 匹配可选的额外参数 ', QMessageBox.Ok' (Group 8) 和 ')'
    
    pattern_msgbox_str = (
        r'(\b(QMessageBox\.(' + r'|'.join(TARGETS_MSGBOX) + r'))\s*\([^,]+,)'
        r'(\s*(".*?"|\'.*?\')\s*,)'
        r'(\s*(".*?"|\'.*?\')\s*)'
        r'((?:,.*)?)\)'
    )

    # 替换函数：
    # m.group(1) = 'QMessageBox.information(self,'
    # m.group(4) = '  "Title"  ' (带逗号)
    # m.group(6) = '  "Message"  '
    # m.group(8) = ', QMessageBox.Ok' (可选)
    # 替换为: 'QMessageBox.information(self, self.tr(  "Title"  ), self.tr(  "Message"  ), QMessageBox.Ok)'
    
    # .strip(',') 是为了去掉 m.group(4) 末尾的逗号
    repl_msgbox = lambda m: (
        f'{m.group(1)}'
        f' self.tr({m.group(4).strip().rstrip(",")}),'
        f' self.tr({m.group(6).strip()})'
        f'{m.group(8) or ""})'
    )
    
    content = re.sub(pattern_msgbox_str, repl_msgbox, content)

    # --- 第 3 步: 保存文件 (如果有更改) ---
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  - 错误: 无法写入 {file_path}: {e}")
            return False
            
    return False

def main():
    """主执行函数"""
    if len(sys.argv) < 2:
        print("用法: python wrap_qt_strings.py /path/to/your/project")
        print(__doc__)
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.is_dir():
        print(f"错误: 目录不存在: {target_dir}")
        sys.exit(1)

    print("="*60)
    print("      Qt 字符串自动包裹脚本 (i18n)")
    print("="*60)
    print(f"目标目录: {target_dir}\n")
    print("警告：此脚本将直接修改您的 .py 文件。")
    print("请确保您已备份或使用了版本控制 (Git)。\n")
    
    try:
        input("按 Enter 键继续，或按 Ctrl+C 取消...")
    except KeyboardInterrupt:
        print("\n操作已取消。")
        sys.exit(0)

    print("\n正在查找和处理 .py 文件...")
    
    processed_count = 0
    modified_files: Set[Path] = set()

    for file_path in target_dir.rglob('*.py'):
        # 简单过滤掉 .venv 或 venv 目录
        if 'venv' in file_path.parts or '.venv' in file_path.parts:
            continue
            
        processed_count += 1
        if process_file(file_path):
            print(f"  [已修改] {file_path.relative_to(target_dir)}")
            modified_files.add(file_path)

    print("\n--- 处理完成 ---")
    print(f"总共扫描了 {processed_count} 个 .py 文件。")
    print(f"总共修改了 {len(modified_files)} 个文件。")

    if modified_files:
        print("\n建议：")
        print("1. 使用 'git diff' 检查更改是否符合预期。")
        print("2. 手动检查被忽略的情况（如 f-strings 或变量）。")

if __name__ == "__main__":
    main()