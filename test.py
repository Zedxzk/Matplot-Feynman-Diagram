#!/usr/bin/env python3
"""
一键创建 feynplot_GUI 项目的目录结构和示例文件
"""

import os
from pathlib import Path

# 定义项目结构
FILES = {
    "feynplot_GUI/feynplot_gui/__init__.py": "",
    "feynplot_GUI/feynplot_gui/canvas_widget.py": '''\
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111)

    def redraw(self, elements, draw_func):
        self.ax.clear()
        draw_func(self.ax, elements)
        self.canvas.draw()
''',
    "feynplot_GUI/feynplot_gui/controller.py": '''\
class Controller:
    def __init__(self, canvas_widget, list_widget, draw_func):
        self.canvas = canvas_widget
        self.list_widget = list_widget
        self.elements = []
        self.draw_func = draw_func

    def add(self, kind):
        name = f"{kind}{len([e for e in self.elements if e.startswith(kind)])+1}"
        self.elements.append(name)
        self.list_widget.addItem(name)
        self.canvas.redraw(self.elements, self.draw_func)
''',
    "feynplot_GUI/feynplot_gui/main_window.py": '''\
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget
from .canvas_widget import CanvasWidget
from .controller import Controller
from .feyn_draw import draw_feyn

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feynman Diagram GUI")
        central = QWidget()
        hbox = QHBoxLayout(central)

        # 左侧按钮区
        left = QVBoxLayout()
        btn_v = QPushButton("添加顶点")
        btn_l = QPushButton("添加线")
        left.addWidget(btn_v)
        left.addWidget(btn_l)
        left.addStretch()

        # 中间绘图区
        canvas = CanvasWidget(self)

        # 右侧列表区
        right = QVBoxLayout()
        listw = QListWidget()
        right.addWidget(listw)
        right.addStretch()

        hbox.addLayout(left)
        hbox.addWidget(canvas, 1)
        hbox.addLayout(right)
        self.setCentralWidget(central)

        # 控制器逻辑
        self.ctrl = Controller(canvas, listw, draw_feyn)
        btn_v.clicked.connect(lambda: self.ctrl.add("顶点"))
        btn_l.clicked.connect(lambda: self.ctrl.add("线"))
''',
    "feynplot_GUI/feynplot_gui/feyn_draw.py": '''\
def draw_feyn(ax, elements):
    for i, e in enumerate(elements):
        if e.startswith("顶点"):
            ax.plot(i, i, 'ro')
        else:
            ax.plot([i-1, i], [i-1, i], 'k-')
    ax.set_xlim(-1, len(elements))
    ax.set_ylim(-1, len(elements))
''',
    "feynplot_GUI/example.py": '''\
import sys
from PySide6.QtWidgets import QApplication
from feynplot_gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(900, 600)
    win.show()
    sys.exit(app.exec())
''',
    "feynplot_GUI/requirements.txt": "pyside6\nmatplotlib\n",
}

def main():
    for path_str, content in FILES.items():
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {path_str}")
    print("\n完成！项目结构已生成于 feynplot_GUI/ 目录下。")

if __name__ == "__main__":
    main()
