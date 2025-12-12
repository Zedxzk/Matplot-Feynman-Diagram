import os
import re

ROOT_DIR = "feynplot_gui"

# 函数或类构造时带字符串参数的模式，例如：QLabel(self.tr("Text"))、setText(self.tr("Text"))
TRANSLATABLE_PATTERNS = [
    r'(?P<prefix>\bQLabel\s*\(|\bQPushButton\s*\(|\bQCheckBox\s*\(|\bQRadioButton\s*\(|\bQGroupBox\s*\(|\bQAction\s*\()(?P<quote>[\'"])(?P<text>.*?)(?P=quote)',
    r'(?P<prefix>\.setText\s*\(|\.setToolTip\s*\(|\.setStatusTip\s*\(|\.setWhatsThis\s*\(|\.setWindowTitle\s*\()(?P<quote>[\'"])(?P<text>.*?)(?P=quote)'
]

def wrap_tr_in_line(line):
    modified = line
    for pattern in TRANSLATABLE_PATTERNS:
        def replacer(match):
            text = match.group('text')
            if 'self.tr(' in text or 'Qt' in text or '%s' in text or '{}' in text:
                return match.group(0)
            return f"{match.group('prefix')}self.tr({match.group('quote')}{text}{match.group('quote')})"
        modified = re.sub(pattern, replacer, modified)
    return modified

def process_py_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified_lines = [wrap_tr_in_line(line) for line in lines]

    if lines != modified_lines:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        print(f"✅ Translated: {filepath}")
    else:
        print(f"⏭️  Skipped:    {filepath} (no change)")

def traverse_directory(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 忽略 __pycache__ 和 discarded 目录
        dirnames[:] = [d for d in dirnames if d not in ('__pycache__', 'discarded')]
        for filename in filenames:
            if filename.endswith('.py'):
                process_py_file(os.path.join(dirpath, filename))

if __name__ == "__main__":
    print(f"🔍 Processing all translatable strings under: {ROOT_DIR}")
    traverse_directory(ROOT_DIR)
    print("\n✨ Done. You can now run:\n  pylupdate6 feynplot_gui/ -ts locale/zh_CN/feynplot_gui.ts")
