from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Signal, QPointF, Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class CanvasWidget(QWidget):
    # 定义 CanvasWidget 自身发出的信号，供 CanvasController 监听
    canvas_clicked = Signal(QPointF)  # 当画布空白处被点击时，发出点击位置（模型坐标）
    object_selected = Signal(str, str) # 当一个对象被选中时，发出对象ID和类型 ("vertex"或"line")
    object_double_clicked = Signal(str, str) # 当一个对象被双击时，发出对象ID和类型
    object_moved = Signal(str, QPointF) # 当一个对象被拖动移动时，发出对象ID和新位置
    selection_cleared = Signal() # 当点击空白区域清除选中时发出

    # 新增：用于平移和缩放的信号
    canvas_panned = Signal(QPointF) # 发出鼠标拖动在画布上的起始数据坐标
    canvas_zoomed = Signal(QPointF, float) # 发出鼠标滚轮位置（数据坐标）和缩放方向 (1.1 或 1/1.1)
    key_delete_pressed = Signal() # 当 Delete/Backspace 键按下时发出

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True) # 启用鼠标跟踪，用于悬停检测等

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240)) # 淡灰色背景
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self._figure = Figure() # Matplotlib Figure 对象
        self._canvas_figure = FigureCanvas(self._figure) # PySide6 包装的 Matplotlib Canvas
        self._axes = self._figure.add_subplot(111) # Matplotlib Axes 对象

        self._canvas_figure.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._canvas_figure.updateGeometry()

        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas_figure)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._current_mode = "select" # 当前画布操作模式 ('select', 'add_vertex', 'add_line', 'move')

        # 鼠标拖动状态（用于对象移动）
        self._is_dragging = False
        self._drag_start_pos_pixels = None # 拖动开始时的像素坐标
        self._dragged_object_id = None
        self._dragged_object_type = None # 拖动对象的类型
        
        # 画布平移状态 (只记录，不实现平移逻辑)
        self._is_panning = False
        self._pan_start_data_pos = None # 平移开始时的 Matplotlib 数据坐标

        self._hit_test_callback = None # 外部传入的 hit_test 函数

        # 连接 Matplotlib 事件监听器
        self._canvas_figure.mpl_connect('button_press_event', self._on_mouse_press)
        self._canvas_figure.mpl_connect('button_release_event', self._on_mouse_release)
        self._canvas_figure.mpl_connect('motion_notify_event', self._on_mouse_move)
        self._canvas_figure.mpl_connect('scroll_event', self._on_mouse_scroll)
        self._canvas_figure.mpl_connect('key_press_event', self._on_key_press)

    def get_figure(self) -> Figure:
        """提供 Matplotlib Figure 对象给 CanvasController。"""
        return self._figure

    def get_axes(self):
        """提供 Matplotlib Axes 对象给 CanvasController。"""
        return self._axes

    def draw_idle_canvas(self):
        """
        触发底层 Matplotlib Canvas 的非阻塞重绘。
        由 CanvasController 调用。
        """
        self._canvas_figure.draw_idle()

    def set_mode(self, mode: str):
        """设置画布的当前操作模式，并更新光标。"""
        self._current_mode = mode
        if mode == "add_vertex":
            self.setCursor(Qt.CrossCursor)
        elif mode == "add_line":
            self.setCursor(Qt.UpArrowCursor)
        elif mode == "move":
            self.setCursor(Qt.OpenHandCursor)
        else: # select
            self.setCursor(Qt.ArrowCursor)

    def set_hit_test_callback(self, callback):
        """设置用于对象点击检测的回调函数。"""
        self._hit_test_callback = callback

    # --- Matplotlib 事件处理 ---
    def _on_mouse_press(self, event):
        if event.inaxes != self._axes: # 确保点击在坐标轴区域内
            return

        x_data, y_data = event.xdata, event.ydata

        if event.button == 1: # 左键点击
            hit_object_id, hit_object_type = self._hit_test_object(x_data, y_data)

            if self._current_mode == "select":
                if hit_object_id:
                    self._is_dragging = True
                    self._drag_start_pos_pixels = QPointF(event.x, event.y)
                    self._dragged_object_id = hit_object_id
                    self._dragged_object_type = hit_object_type 

                    self.object_selected.emit(hit_object_id, hit_object_type)
                else:
                    self._is_panning = True # 标记开始平移
                    self._pan_start_data_pos = QPointF(x_data, y_data) # 记录起始数据坐标
                    self.setCursor(Qt.ClosedHandCursor) # 更改光标为抓手
                    self.selection_cleared.emit() # 点击空白处，清除选中
                    self._is_dragging = False # 确保没有同时拖动对象
                    
            elif self._current_mode == "add_vertex":
                self.canvas_clicked.emit(QPointF(x_data, y_data))
            elif self._current_mode == "add_line":
                if hit_object_id and hit_object_type == "vertex":
                    self.object_selected.emit(hit_object_id, hit_object_type)
                else:
                    # 如果在添加线条模式下点击空白处或非顶点，则也视为画布点击事件
                    self.canvas_clicked.emit(QPointF(x_data, y_data))

    def _on_mouse_release(self, event):
        if event.button == 1: # 左键释放
            if self._is_dragging:
                self._is_dragging = False
                self._dragged_object_id = None
                self._dragged_object_type = None 
                
            if self._is_panning:
                self._is_panning = False
                self._pan_start_data_pos = None
                # 恢复光标，如果当前模式是 'select' 且没有其他操作在进行
                if self._current_mode == "select":
                    x_data, y_data = event.xdata, event.ydata
                    if x_data is not None and y_data is not None:
                        # 检查鼠标释放时是否在对象上，以决定最终光标状态
                        hit_object_id, _ = self._hit_test_object(x_data, y_data)
                        if hit_object_id:
                            self.setCursor(Qt.PointingHandCursor)
                        else:
                            self.setCursor(Qt.ArrowCursor)
                    else:
                         self.setCursor(Qt.ArrowCursor)


            # 处理双击事件（在非拖动结束后）
            if event.dblclick:
                x_data, y_data = event.xdata, event.ydata
                if x_data is not None and y_data is not None:
                    hit_object_id, hit_object_type = self._hit_test_object(x_data, y_data)
                    if hit_object_id:
                        self.object_double_clicked.emit(hit_object_id, hit_object_type)

    def _on_mouse_move(self, event):
        if event.inaxes != self._axes:
            # 只有当不在拖动或平移时才重置光标
            if not self._is_dragging and not self._is_panning:
                self.setCursor(Qt.ArrowCursor)
            return

        x_data, y_data = event.xdata, event.ydata
        
        # 确保 x_data 和 y_data 不为 None
        if x_data is None or y_data is None:
            return

        if self._is_dragging and self._dragged_object_id and self._dragged_object_type == "vertex":
            self.setCursor(Qt.ClosedHandCursor)
            # 发出对象移动信号，不在这里直接修改坐标
            new_model_pos = QPointF(x_data, y_data)
            self.object_moved.emit(self._dragged_object_id, new_model_pos)
        elif self._is_panning:
            self.setCursor(Qt.ClosedHandCursor) # 平移时光标保持为抓手
            # 发出画布平移信号，将起始位置和当前位置传递给控制器
            self.canvas_panned.emit(self._pan_start_data_pos) # 发送起始点，控制器将用当前点计算位移
        elif self._current_mode == "move":
            self.setCursor(Qt.OpenHandCursor)
        elif self._current_mode == "add_vertex":
            self.setCursor(Qt.CrossCursor)
        elif self._current_mode == "add_line":
            self.setCursor(Qt.UpArrowCursor)
        else: # select mode, for hover effect
            hit_object_id, _ = self._hit_test_object(x_data, y_data)
            if hit_object_id:
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def _on_mouse_scroll(self, event):
        """处理鼠标滚轮事件进行缩放，只发出信号。"""
        if event.inaxes != self._axes:
            return

        x_mouse, y_mouse = event.xdata, event.ydata
        
        if x_mouse is None or y_mouse is None:
            return

        scale_factor = 1.1 if event.button == 'up' else 1 / 1.1
        # 发出画布缩放信号
        self.canvas_zoomed.emit(QPointF(x_mouse, y_mouse), scale_factor)

    def _on_key_press(self, event):
        """处理键盘事件，只发出信号。"""
        if event.key == 'delete' or event.key == 'backspace':
            self.key_delete_pressed.emit() # 发出删除键被按下的信号
            self.selection_cleared.emit() # 通常删除后会清除选中状态

    def _hit_test_object(self, x: float, y: float) -> (str, str):
        """
        这个方法将调用由 CanvasController 传入的 MatplotlibBackend 的 hit_test 方法。
        """
        if self._hit_test_callback: # 确保回调函数已设置
            return self._hit_test_callback(x, y)
        return None, None # 如果回调未设置，返回None