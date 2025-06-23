from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys

class FeynmanEditor(QMainWindow):
    def __init__(self, draw_func):
        super().__init__()
        self.setWindowTitle("Feynman Diagram Editor")
        self.resize(1000,600)

        central = QWidget()
        hbox = QHBoxLayout(central)

        # 左侧按钮区
        vbox_left = QVBoxLayout()
        btn_vertex = QPushButton("添加顶点")
        btn_line = QPushButton("添加线")
        vbox_left.addWidget(btn_vertex)
        vbox_left.addWidget(btn_line)
        vbox_left.addStretch()

        # 中间绘图区
        self.fig = Figure(figsize=(5,5))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        # 右侧列表
        vbox_right = QVBoxLayout()
        self.listwidget = QListWidget()
        vbox_right.addWidget(self.listwidget)
        vbox_right.addStretch()

        hbox.addLayout(vbox_left)
        hbox.addWidget(self.canvas, 1)
        hbox.addLayout(vbox_right)

        self.setCentralWidget(central)

        # 数据与交互
        self.elements = []
        self.draw_func = draw_func
        btn_vertex.clicked.connect(lambda: self.add("顶点"))
        btn_line.clicked.connect(lambda: self.add("线"))

    def add(self, kind):
        name = f"{kind}{len([e for e in self.elements if e.startswith(kind)])+1}"
        self.elements.append(name)
        self.listwidget.addItem(name)
        self.redraw()

    def redraw(self):
        self.ax.clear()
        self.draw_func(self.ax, self.elements)
        self.canvas.draw()

def draw_feyn(ax, elems):
    for i,e in enumerate(elems):
        if e.startswith("顶点"):
            ax.plot(i, i, 'ro')
        else:
            ax.plot([i-1, i], [i-1, i], 'k-')
    ax.set_xlim(-1, len(elems))
    ax.set_ylim(-1, len(elems))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FeynmanEditor(draw_feyn)
    win.show()
    app.exec()
