from PySide6.QtCore import QPointF, Signal, Qt, QTime, QLineF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, Callable
from feynplot_gui.default.default_settings import canvas_widget_default_settings as default_settings

class CanvasWidget(QWidget):
    # Various user interaction signals
    canvas_clicked = Signal(QPointF)
    object_selected = Signal(str, str)
    object_double_clicked = Signal(str, str)
    object_moved = Signal(str, QPointF)
    selection_cleared = Signal()
    key_delete_pressed = Signal()
    blank_double_clicked = Signal(QPointF)
    # Pan and zoom signals
    canvas_panned = Signal(QPointF, QPointF) # 更改：现在平移信号传递起始和结束数据点
    canvas_zoomed = Signal(QPointF, float)
    
    view_updated = Signal(dict) # 传递一个字典，包含 target_xlim 和 target_ylim
    object_edited = Signal(str, str)
    object_deleted = Signal(str, str)
    mouse_released = Signal()
    
    add_line_from_vertex_requested = Signal(str) # 传递起始顶点的ID

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 10), dpi=150)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setParent(self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Connect Matplotlib events
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('scroll_event', self._on_mouse_scroll)

        # Internal state variables
        self._is_panning = False
        self._is_dragging_object = False
        self._dragged_object_id: Optional[str] = None
        self._dragged_object_type: Optional[str] = None
        self._mouse_press_data_pos: Optional[QPointF] = None # 记录鼠标按下时的**数据坐标**
        self._mouse_press_pixel_pos: Optional[QPointF] = None # 记录鼠标按下时的**像素坐标**
        self._is_drag_event = False # 用于标记当前操作是否被识别为拖动
        
        self._last_click_time = QTime.currentTime().msecsSinceStartOfDay()
        self._current_mode = "select"
        self._hit_test_callback: Optional[Callable[[float, float], tuple[Optional[str], Optional[str]]]] = None

        # Configurable drag threshold (in pixels)
        self.DRAG_THRESHOLD_PIXELS = default_settings['DRAG_THRESHOLD_PIXELS'] # 鼠标移动超过5像素就认为是拖动

        # --- 新增：用于限制 _on_mouse_move 信号发出频率的变量 ---
        self._last_signal_time = 0  # 记录上次发出 object_moved 或 canvas_panned 信号的时间 (毫秒)
        self.SIGNAL_INTERVAL_MS = default_settings['SIGNAL_INTERVAL_MS'] # 信号发出的最小时间间隔 (毫秒)
        # --- 结束新增 ---

        # Axes initial setup
        self.axes.set_aspect('equal', adjustable='box')
        self.axes.set_axis_off()
        self.figure.tight_layout()

    def get_figure(self) -> Figure:
        """返回 Matplotlib Figure 对象。"""
        return self.figure

    def get_axes(self) -> Axes:
        """返回 Matplotlib Axes 对象。"""
        return self.axes

    def set_mode(self, mode: str):
        """
        允许 CanvasController 设置当前模式，并根据模式调整光标。
        """
        self._current_mode = mode
        if mode == "add_vertex":
            self.setCursor(Qt.CrossCursor)
        elif mode == "add_line":
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_hit_test_callback(self, callback: Callable[[float, float], tuple[Optional[str], Optional[str]]]):
        """允许 CanvasController 提供一个点击检测函数。"""
        self._hit_test_callback = callback

    def draw_idle_canvas(self):
        """触发 Matplotlib 画布的空闲重绘。"""
        self.canvas.draw_idle()

    # --- 鼠标事件处理函数 ---
    def _on_mouse_press(self, event):
        if event.inaxes != self.axes or event.xdata is None or event.ydata is None:
            return

        self._mouse_press_data_pos = QPointF(event.xdata, event.ydata)
        self._mouse_press_pixel_pos = QPointF(event.x, event.y) # 记录像素坐标
        self._is_drag_event = False # 假定开始不是拖动，直到移动距离超过阈值

        current_time = QTime.currentTime().msecsSinceStartOfDay()
        double_click_interval = default_settings['DOUBLE_CLICK_INTERVAL_MS']# 毫秒

        # 双击检查 (使用 QTime)
        if event.button == 1 and (current_time - self._last_click_time) < double_click_interval:
            if self._hit_test_callback:
                item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                if item_id:
                    self.object_double_clicked.emit(item_id, item_type)
                # If no item_id, it means a blank area was double-clicked
                if not item_id:
                    # 发出带坐标的 blank_double_clicked 信号
                    self.blank_double_clicked.emit(self._mouse_press_data_pos)
            else: # No hit_test_callback means we assume it's blank
                self.blank_double_clicked.emit(self._mouse_press_data_pos)

            self._last_click_time = 0
            return # 双击事件处理完毕，直接返回，不触发单击/拖拽逻辑
        else:
            self._last_click_time = current_time # 更新上次单击时间

        # 以下逻辑在鼠标释放时根据 _is_drag_event 决定是否发出点击信号
        if event.button == 1:  # 左键
            if self._current_mode == "select":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id:
                        self._is_dragging_object = True
                        self._dragged_object_id = item_id
                        self._dragged_object_type = item_type
                        self.object_selected.emit(item_id, item_type) # 单击选中 (此处仍可发出，拖动后不会再发)
                        self.setCursor(Qt.SizeAllCursor)
                    else:
                        self.selection_cleared.emit()
                        self._is_panning = True
                        # 不在此处立即发出 canvas_panned，留待 mouse_move 处理
                        self.setCursor(Qt.ClosedHandCursor)
                else: # 没有点击测试回调，直接进入平移模式
                    self._is_panning = True
                    # 不在此处立即发出 canvas_panned，留待 mouse_move 处理
                    self.setCursor(Qt.ClosedHandCursor)
            elif self._current_mode == "add_vertex":
                # 在 add_vertex 模式下，左键按下不立即发出 canvas_clicked
                # 而是在 mouse_release 时发出
                pass
            elif self._current_mode == "add_line":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id and item_type == "vertex":
                        self.object_selected.emit(item_id, item_type)
                    else:
                        # 延迟 canvas_clicked 的发出，如果后续是拖动就不发
                        pass 
                else:
                    # 延迟 canvas_clicked 的发出，如果后续是拖动就不发
                    pass
        
        elif event.button == 3:  # 右键
            if self._current_mode == "select":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id:
                        self.object_selected.emit(item_id, item_type) # 右键也选中对象
                        self._show_context_menu(event, item_id, item_type)
                    else:
                        self.selection_cleared.emit()
                else:
                    self.selection_cleared.emit()


    def _on_mouse_release(self, event):
        if self._is_dragging_object and self._is_drag_event:
            self.mouse_released.emit()
        if event.inaxes != self.axes or self._mouse_press_data_pos is None:
            # 如果不是在 Axes 内部释放，或者没有记录按下时的位置（例如双击后立即返回）
            self._is_panning = False
            self._is_dragging_object = False
            self._dragged_object_id = None
            self._dragged_object_type = None
            self._mouse_press_data_pos = None
            self._mouse_press_pixel_pos = None
            self._is_drag_event = False
            self.set_mode(self._current_mode) # 恢复光标
            # self.mouse_released.emit() # 确保总是在此方法结束时发出
            return

        current_mouse_data_pos = QPointF(event.xdata, event.ydata) if event.xdata is not None and event.ydata is not None else self._mouse_press_data_pos
        current_mouse_pixel_pos = QPointF(event.x, event.y) if event.x is not None and event.y is not None else self._mouse_press_pixel_pos

        # 计算像素距离，判断是否是拖动
        if self._mouse_press_pixel_pos and current_mouse_pixel_pos:
            pixel_distance = QLineF(self._mouse_press_pixel_pos, current_mouse_pixel_pos).length()
            if pixel_distance > self.DRAG_THRESHOLD_PIXELS:
                self._is_drag_event = True

        # 如果是拖动事件，则不触发单击信号
        if self._is_drag_event:
            # 拖动结束，重置所有拖动状态
            self._is_panning = False
            self._is_dragging_object = False
            self._dragged_object_id = None
            self._dragged_object_type = None
            self._mouse_press_data_pos = None
            self._mouse_press_pixel_pos = None
            self._is_drag_event = False # 重置拖动标记
            self.set_mode(self._current_mode) # 恢复光标
            # self.mouse_released.emit() # 确保总是在此方法结束时发出
            return # 拖动事件，不视为点击

        # 以下是点击事件处理逻辑
        if event.button == 1:  # 左键点击
            if self._current_mode == "select":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id:
                        # 确保单击对象时，如果之前未选中，现在可以选中。
                        # 如果在press时已发出object_selected，这里无需重复。
                        pass
                    else:
                        # 点击空白区域，发出 canvas_clicked
                        self.canvas_clicked.emit(current_mouse_data_pos)
                else:
                    self.canvas_clicked.emit(current_mouse_data_pos) # 没有 hit test 回调，直接认为点击了画布

            elif self._current_mode == "add_vertex":
                if event.xdata is not None and event.ydata is not None:
                    self.canvas_clicked.emit(QPointF(event.xdata, event.ydata))
            elif self._current_mode == "add_line":
                if self._hit_test_callback:
                    item_id, item_type = self._hit_test_callback(event.xdata, event.ydata)
                    if item_id and item_type == "vertex":
                        # 顶点被选中，无需在此发出 canvas_clicked
                        pass
                    else:
                        # 点击了空白或非顶点区域，发出 canvas_clicked
                        self.canvas_clicked.emit(current_mouse_data_pos)
                else:
                    self.canvas_clicked.emit(current_mouse_data_pos)

        # 重置所有拖动相关的内部状态，无论是否是拖动事件
        self._is_panning = False
        self._is_dragging_object = False
        self._dragged_object_id = None
        self._dragged_object_type = None
        self._mouse_press_data_pos = None
        self._mouse_press_pixel_pos = None
        self._is_drag_event = False # 确保每次释放后重置
        self.set_mode(self._current_mode) # 恢复光标

    def _on_mouse_move(self, event):
        if event.inaxes != self.axes or event.xdata is None or event.ydata is None:
            return

        current_mouse_data_pos = QPointF(event.xdata, event.ydata)
        current_mouse_pixel_pos = QPointF(event.x, event.y)

        # 如果鼠标按下位置已记录，且当前是拖动模式（_is_dragging_object 或 _is_panning）
        # 并且移动距离超过阈值，则标记为拖动事件
        if self._mouse_press_pixel_pos and current_mouse_pixel_pos:
            pixel_distance = QLineF(self._mouse_press_pixel_pos, current_mouse_pixel_pos).length()
            if pixel_distance > self.DRAG_THRESHOLD_PIXELS:
                self._is_drag_event = True # 标记为拖动事件

        current_time = QTime.currentTime().msecsSinceStartOfDay()

        # 检查是否满足发送信号的最小时间间隔
        if (current_time - self._last_signal_time) < self.SIGNAL_INTERVAL_MS:
            return # 如果间隔不足，则不发送信号，直接返回

        # 更新上次发送信号的时间
        self._last_signal_time = current_time

        if self._is_dragging_object and self._dragged_object_id:
            # 发出 object_moved 信号，通知 CanvasController 更新模型中的对象位置
            self.object_moved.emit(self._dragged_object_id, current_mouse_data_pos)
            self.draw_idle_canvas() 
        elif self._is_panning and self._is_drag_event:
            # 确认是空白区域平移，并且达到拖动阈值
            # 持续发出平移信号，通知控制器平移
            self.canvas_panned.emit(self._mouse_press_data_pos, current_mouse_data_pos)

            
    def _on_mouse_scroll(self, event):
        """
        处理鼠标滚轮事件，用于缩放。
        event.step > 0 表示滚轮向上滚动 (放大)
        event.step < 0 表示滚轮向下滚动 (缩小)
        """
        if event.inaxes != self.axes:
            return

        if event.xdata is None or event.ydata is None:
            xlim = self.axes.get_xlim()
            ylim = self.axes.get_ylim()
            mouse_x = (xlim[0] + xlim[1]) / 2
            mouse_y = (ylim[0] + ylim[1]) / 2
        else:
            mouse_x, mouse_y = event.xdata, event.ydata

        zoom_factor = 1.08

        if event.step > 0: # Scroll up (zoom in)
            scale_factor = 1.0 / zoom_factor
        else: # Scroll down (zoom out)
            scale_factor = zoom_factor

        self.canvas_zoomed.emit(QPointF(mouse_x, mouse_y), scale_factor)

    # --- 右键菜单相关方法 ---
    def _show_context_menu(self, event, item_id: str, item_type: str):
        menu = QMenu(self)

        # 【新增】如果点击的是顶点，添加“添加线条”选项
        if item_type == "vertex":
            add_line_action = QAction("添加线条", self)
            # 连接到新的槽函数，该槽函数将发出 add_line_from_vertex_requested 信号
            add_line_action.triggered.connect(lambda: self._on_add_line_from_vertex_action(item_id))
            menu.addAction(add_line_action)
            # 添加一个分隔符，使菜单更清晰
            menu.addSeparator()

        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self._on_edit_object_action(item_id, item_type))
        menu.addAction(edit_action)

        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._on_delete_object_action(item_id, item_type))
        menu.addAction(delete_action)

        menu.exec(event.guiEvent.globalPos())

    def _on_edit_object_action(self, item_id: str, item_type: str):
        """响应 '编辑' 菜单项点击的槽函数。"""
        print(f"请求编辑 {item_type} ID: {item_id}")
        self.object_edited.emit(item_id, item_type)

    def _on_delete_object_action(self, item_id: str, item_type: str):
        """响应 '删除' 菜单项点击的槽函数。"""
        print(f"请求删除 {item_type} ID: {item_id}")
        self.object_deleted.emit(item_id, item_type)

    # --- 【新增】处理“添加线条”菜单项点击的槽函数 ---
    def _on_add_line_from_vertex_action(self, vertex_id: str):
        """响应 '添加线条' 菜单项点击的槽函数。"""
        print(f"请求从顶点 {vertex_id} 添加线条")
        # 发出信号，通知控制器从这个顶点开始添加线条
        self.add_line_from_vertex_requested.emit(vertex_id)

    def set_update_interval(self, interval_ms: int):
        """设置更新视图的最小时间间隔 (毫秒)。"""
        self.SIGNAL_INTERVAL_MS = interval_ms