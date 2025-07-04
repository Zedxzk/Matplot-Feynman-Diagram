import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# --- 全局变量控制初始网格状态 ---
init_grid_state = False 

# --- Matplotlib 全局参数设置 ---
plt.rcParams['font.family'] = ['SimHei', 'FangSong', 'KaiTi', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False 

class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matplotlib + PySide6 网格开关示例 (已修正)")
        self.setGeometry(100, 100, 800, 600)

        # 1. 创建 Matplotlib 图形和坐标轴
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # 2. 创建一个 QVBoxLayout 来放置画布和复选框
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.canvas)

        # 3. 添加一个 QCheckBox 来控制网格显示
        self.grid_checkbox = QCheckBox("显示网格")
        self.grid_checkbox.setChecked(init_grid_state) # 设置复选框的初始状态
        # 连接信号到统一的重绘函数
        self.grid_checkbox.stateChanged.connect(self._update_canvas) 
        main_layout.addWidget(self.grid_checkbox)

        # 4. 创建一个 QWidget 作为中心部件的容器
        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        self.setCentralWidget(container_widget)

        # 5. 执行初次绘制
        self._update_canvas()

    def _update_canvas(self):
        """
        统一的画布更新函数。
        该函数负责根据所有UI控件的当前状态，从头开始重绘整个图形。
        """
        # a. 清除坐标轴上的所有旧内容
        self.ax.clear()

        # b. 绘制核心数据内容
        self.ax.plot([1, 2, 3, 4], [10, 20, 25, 30], 'o-', label="简单数据")
        self.ax.set_xlabel('X 轴')
        self.ax.set_ylabel('Y 轴')
        self.ax.set_title('简单绘图')
        self.ax.legend()

        # c. 根据复选框的当前状态来决定是否显示网格
        show_grid = self.grid_checkbox.isChecked()
        self.ax.grid(show_grid)

        # d. 调整布局并触发画布重绘
        self.figure.tight_layout()
        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec())