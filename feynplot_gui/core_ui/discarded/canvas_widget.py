# feynplot_GUI/feynplot_gui/canvas_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPalette # 导入 QPalette 来设置背景
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# 导入你的 MatplotlibBackend 类
from feynplot.drawing.renderer import MatplotlibBackend 
from feynplot.core.diagram import FeynmanDiagram

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 根据父部件的背景角色设置自身背景，或使用默认窗口背景
        if self.parent():
            self.setBackgroundRole(self.parent().backgroundRole())
        else:
            self.setBackgroundRole(QPalette.Window)
            self.setAutoFillBackground(True) # 自动填充背景

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111) # 将 axes 命名为 ax
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 实例化 MatplotlibBackend，传入我们创建的 fig 和 ax
        self._matplotlib_backend = MatplotlibBackend(fig=self.fig, ax=self.ax) 
        
        self._diagram_data: FeynmanDiagram = None 
        self.setMouseTracking(True) # 启用鼠标跟踪，即使没有按钮按下也能接收鼠标移动事件

        # 设置 Matplotlib 坐标轴的初始属性
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.grid(True) # 显示网格

        # 用于存储高亮的艺术家（例如，高亮的顶点或线条）
        self._highlighted_artist = None


    def set_diagram_data(self, diagram_data: FeynmanDiagram):
        """设置费曼图数据模型，并在设置后重绘画布。"""
        self._diagram_data = diagram_data
        self.update_canvas() # 数据设置后立即重绘

    def update_canvas(self):
        """
        触发 Matplotlib 后端的渲染。
        """
        if self._diagram_data:
            # 清除之前的绘图，然后让 MatplotlibBackend 重新绘制
            self._matplotlib_backend.ax.clear()
            # 重新设置坐标轴属性，确保每次清除后视图一致
            self._matplotlib_backend.ax.set_aspect('equal', adjustable='box')
            # 确保 xlim/ylim 在清除后保留或重置到合适的值
            # 这里需要注意，如果鼠标平移/缩放改变了xlim/ylim，这里不应该直接重置，
            # 而应该在绘制前保存并恢复它们，或者让后端处理。
            # 为了简化，假设MatplotlibBackend会处理轴的设置。
            # 实际项目中，你可能需要传递当前的 xlim/ylim 给 render 方法，让它保持视图状态
            
            self._matplotlib_backend.render(self._diagram_data.vertices, self._diagram_data.lines)
            
            # 如果有高亮的元素，确保在后端绘制后重新绘制高亮
            if self._highlighted_artist:
                # 获取高亮元素的绘图参数，并调整以显示高亮效果
                if hasattr(self._highlighted_artist, 'x'): # 是顶点
                    self._matplotlib_backend.ax.plot(
                        self._highlighted_artist.x, self._highlighted_artist.y,
                        'o', color='yellow', markersize=self._highlighted_artist.size / 10 + 5,
                        markeredgecolor='orange', linewidth=2, zorder=10 # 增大尺寸和zorder
                    )
                elif hasattr(self._highlighted_artist, 'v_start'): # 是线条
                    start_x, start_y = self._highlighted_artist.v_start.x, self._highlighted_artist.v_start.y
                    end_x, end_y = self._highlighted_artist.v_end.x, self._highlighted_artist.v_end.y
                    self._matplotlib_backend.ax.plot(
                        [start_x, end_x], [start_y, end_y],
                        color='yellow', linewidth=5, zorder=10 # 增大线宽和zorder
                    )
            
            # 确保 CanvasQTAgg 知道它需要重绘
            self.canvas.draw_idle() 
        else:
            # 如果没有数据，清空 Matplotlib 图
            self._matplotlib_backend.ax.clear()
            self._matplotlib_backend.ax.set_aspect('equal', adjustable='box')
            self._matplotlib_backend.ax.set_axis_off() # 隐藏坐标轴
            self._matplotlib_backend.fig.tight_layout()
            self.canvas.draw_idle()

    def set_highlighted_artist(self, artist):
        """设置当前高亮的 Matplotlib 艺术家对象 (例如，由 Backend 返回的 Plot 对象)。"""
        self._highlighted_artist = artist
        self.update_canvas() # 重绘以显示高亮

    def clear_highlight(self):
        """清除高亮。"""
        self._highlighted_artist = None
        self.update_canvas() # 重绘以清除高亮

    # 将 CanvasWidget 的鼠标和滚轮事件重定向到 Controller
    # 注意：这些方法本身不会做太多事情，它们会将事件传递给 Controller 处理。
    # Controller 将会通过 self.canvas.mousePressEvent = self._mouse_press_event 
    # 这样的方式来覆盖这些方法。
    # 理论上，Matplotlib 的 FigureCanvas 也有自己的事件处理，
    # 但为了统一管理，我们通过 Controller 来处理。

    def mousePressEvent(self, event):
        # 此方法被 Controller 的 connect_events 覆盖
        super().mousePressEvent(event) 
    def mouseMoveEvent(self, event):
        # 此方法被 Controller 的 connect_events 覆盖
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        # 此方法被 Controller 的 connect_events 覆盖
        super().mouseReleaseEvent(event)
    def wheelEvent(self, event):
        # 此方法被 Controller 的 connect_events 覆盖
        super().wheelEvent(event)