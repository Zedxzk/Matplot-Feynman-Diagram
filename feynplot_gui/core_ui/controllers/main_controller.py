# feynplot_GUI/feynplot_gui/controllers/main_controller.py
from typing import Optional, Tuple, Dict, Any, Union
from feynplot_gui.debug_utils import cout, cout3
from PySide6.QtCore import QObject, Signal, QPointF, Qt, QEvent
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QFileDialog, QApplication,
    QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit, QComboBox,
    QListWidget,
)
from PySide6.QtGui import QShortcut, QKeySequence
import os

# 导入所有控制器
from .canvas_controller import CanvasController
from .navigation_bar_controller import NavigationBarController
from .toolbox_controller import ToolboxController
from .vertex_controller import VertexController
from .line_controller import LineController
from feynplot_gui.core_ui.controllers.other_texts_controller import OtherTextsController

# 导入核心模型类和其组成部分
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import Line, FermionLine, PhotonLine, GluonLine, LineStyle
from feynplot.core.extra_text_element import TextElement

# 导入主窗口 (方便类型提示和访问其子组件实例)
from feynplot_gui.core_ui.widgets.main_window import MainWindow
from feynplot_gui.core_ui.msg_box_utils import MsgBox
# 导入对话框，因为 MainController 现在负责它们的创建和数据显示
from feynplot_gui.core_ui.dialogs.add_vertex_dialog import AddVertexDialog
# from feynplot_gui.core_ui.dialogs.edit_vertex_dialog import EditVertexDialog
from feynplot_gui.core_ui.dialogs.add_line_dialog import AddLineDialog
# from feynplot_gui.core_ui.dialogs.edit_line_dialog import EditLineDialog
from feynplot_gui.core_ui.dialogs.delete_vertex_dialog import DeleteVertexDialog
from feynplot_gui.core_ui.dialogs.delete_line_dialog import DeleteLineDialog
from feynplot_gui.default.default_settings import CANVAS_CONTROLLER_DEFAULTS

class MainController(QObject):
    # 定义 MainController 自身发出的信号
    # diagram_model_updated = Signal() # 如果 diagram_model 不发信号，这个信号的作用会减弱，或者改为在每次更新视图时发出
    selection_changed = Signal(object)  # 当选中对象发生变化时发出 (发送 Vertex 或 Line 实例)
    status_message = Signal(str)        # 用于在状态栏显示信息

    def __init__(self, main_window: MainWindow):
        super().__init__()

        self.main_window = main_window
        self.diagram_model = FeynmanDiagram() # 实例化你的核心费曼图模型
        cout3("创建核心费曼图模型")
        # 内部跟踪当前选中项
        self._current_selected_item = None
        # 选中项的 ID（用于 label 高亮，如 vlabel:vertex_1、llabel:line_1）
        self._current_selected_item_id = None
        # 跟踪当前工具模式，MainController负责管理并转发给CanvasController
        self._current_tool_mode = "select" # 默认选择模式
        self.always_auto_scale = False  # 始终自动调整画布

        # 实例化所有子控制器，并传递必要的依赖（模型、UI组件实例、MainController自身）

        self.vertex_controller = VertexController(
            diagram_model=self.diagram_model,
            vertex_list_widget=self.main_window.vertex_list_widget_instance,
            main_controller=self
        )
        self.line_controller = LineController(
            diagram_model=self.diagram_model,
            line_list_widget=self.main_window.line_list_widget_instance,
            main_controller=self
        )
        self.toolbox_controller = ToolboxController(
            toolbox_widget=self.main_window.toolbox_widget_instance,
            main_controller=self
        )
        self.navigation_bar_controller = NavigationBarController(
            navigation_bar_widget=self.main_window.navigation_bar_widget_instance,
            main_controller=self
        )
                # --- 新增 OtherTextsController 的初始化 ---
        self.other_texts_controller = OtherTextsController(
            other_texts_widget=self.main_window.other_texts_widget, # 传入 OtherTextsWidget 实例
            main_controller=self,                       # 传入 MainController 自身
        )
        self.canvas_controller = CanvasController(
            diagram_model=self.diagram_model,
            canvas_widget=self.main_window.canvas_widget_instance,
            main_controller=self
        )
        # 初始加载或设置一些默认数据
        self._initialize_diagram_data()

        # 连接所有 UI 信号到控制器槽函数
        self._link_controllers_signals()

        # Delete/Backspace 由 eventFilter 处理（可区分编辑控件，避免在输入框内误触发删除）
        # Ctrl+S/Ctrl+Shift+S：以 QApplication 为父级，确保任意焦点下均可响应
        app = QApplication.instance()
        if app:
            self._save_project_shortcut = QShortcut(QKeySequence.StandardKey.Save, app)
            self._save_project_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            self._save_project_shortcut.activated.connect(self.navigation_bar_controller._on_save_project_ui_triggered)
            self._save_image_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), app)
            self._save_image_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            self._save_image_shortcut.activated.connect(self.save_diagram_to_file)
        else:
            self._save_project_shortcut = QShortcut(QKeySequence.StandardKey.Save, main_window)
            self._save_project_shortcut.activated.connect(self.navigation_bar_controller._on_save_project_ui_triggered)
            self._save_image_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), main_window)
            self._save_image_shortcut.activated.connect(self.save_diagram_to_file)

        # 方向键、F2、Delete：安装到 QApplication 以在事件到达列表等控件前拦截
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
        else:
            main_window.installEventFilter(self)

        # 连接 MainController 自身的信号到主窗口的状态栏
        # self.status_message.connect(self.main_window.show_status_message)

        # 初始更新所有视图（自动调整画布在窗口显示后通过 QTimer 模拟点击触发）
        self.update_all_views()
        self.status_message.emit("应用程序已启动。")
        # 设置一些属性
        self.zoom_times = 0
        self.absolute_fontsize = False

    def _link_controllers_signals(self):
        """连接所有UI组件发出的信号到对应的控制器槽函数。"""

        # --- CanvasController 信号连接 ---
        # CanvasController 的 object_selected 信号可以传递选中对象或 None
        # self.canvas_controller.object_selected.connect(self.select_item)
        self.canvas_controller.line_creation_completed.connect(self.add_line_between_vertices)

        # ... (ToolboxWidget 和 NavigationBarWidget 的连接保持不变) ...
        self.main_window.toolbox_widget_instance.add_vertex_requested.connect(self.start_add_vertex_process)
        self.main_window.toolbox_widget_instance.add_line_requested.connect(self.start_add_line_process)
        self.main_window.toolbox_widget_instance.delete_vertex_requested.connect(self.delete_selected_vertex)
        self.main_window.toolbox_widget_instance.delete_line_requested.connect(self.delete_selected_line)
        self.main_window.toolbox_widget_instance.save_diagram_requested.connect(self.save_diagram_to_file)


        # --- NavigationBarWidget 信号连接 ---
        self.main_window.navigation_bar_widget_instance.add_vertex_button_clicked.connect(self.start_add_vertex_process)
        self.main_window.navigation_bar_widget_instance.add_line_button_clicked.connect(self.start_add_line_process)
        # --- VertexListWidget 信号连接 ---
        # 用户的列表项点击事件 (现在只在 mousePressEvent 中发出)
        self.main_window.vertex_list_widget_instance.vertex_selected.connect(self.select_item)
        # 用户点击列表空白处事件 (现在只在 mousePressEvent 中发出)
        self.main_window.vertex_list_widget_instance.list_blank_clicked.connect(lambda: self.select_item(None))
        # 双击列表项事件
        # self.main_window.vertex_list_widget_instance.vertex_double_clicked.connect(self._handle_list_vertex_double_clicked)
        # 右键菜单操作
        # self.main_window.vertex_list_widget_instance.edit_vertex_requested.connect(self.select_item)
        # self.main_window.vertex_list_widget_instance.delete_vertex_requested.connect(self.delete_selected_vertex)
        # self.main_window.vertex_list_widget_instance.search_vertex_requested.connect(self.search_vertex_by_keyword)
        self.canvas_controller.canvas_widget.canvas_panned.connect(self._update_canvas_range_on_navigation_bar)
        self.canvas_controller.canvas_widget.canvas_panned.connect(self._on_canvas_zoomed_or_panned)
        self.canvas_controller.canvas_widget.canvas_zoomed.connect(self._on_canvas_zoomed_or_panned)

        # --- LineListWidget 信号连接 ---
        # 用户的列表项点击事件 (现在只在 mousePressEvent 中发出)
        self.main_window.line_list_widget_instance.line_selected.connect(self.select_item)
        # 用户点击列表空白处事件 (现在只在 mousePressEvent 中发出)
        self.main_window.line_list_widget_instance.list_blank_clicked.connect(lambda: self.select_item(None))
        # 双击列表项事件
        self.main_window.line_list_widget_instance.line_double_clicked.connect(self._handle_list_line_double_clicked)

        # 画布右键菜单触发的操作（与菜单/工具栏等效）
        self.main_window.canvas_widget_instance.context_auto_scale_requested.connect(
            self.main_window.navigation_bar_widget_instance.toggle_auto_scale_requested.emit
        )
        self.main_window.canvas_widget_instance.context_toggle_grid_requested.connect(
            self.canvas_controller.toggle_grid_visibility
        )
        self.main_window.canvas_widget_instance.context_add_vertex_requested.connect(self.start_add_vertex_process)
        self.main_window.canvas_widget_instance.context_add_text_requested.connect(
            self.other_texts_controller._on_request_add_new_text
        )
        self.main_window.navigation_bar_widget_instance.toggle_always_auto_scale.connect(self._on_always_auto_scale_toggled)

    def _on_always_auto_scale_toggled(self, checked: bool):
        """当“始终自动调整画布”复选框切换时更新标志；勾选时触发一次重绘。"""
        self.always_auto_scale = bool(checked)
        self.status_message.emit(self.tr("始终自动调整画布") + ": " + (self.tr("开") if checked else self.tr("关")))
        if checked:
            self.update_all_views(canvas_options={'auto_scale': True})

    def _on_canvas_zoomed_or_panned(self, *args):
        """滚轮缩放或拖动画布时自动取消勾选“始终自动调整画布”。"""
        if not self.always_auto_scale:
            return
        self.always_auto_scale = False
        cb = self.main_window.navigation_bar_widget_instance.always_auto_scale_checkbox
        if cb:
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)

    # --- MainController 内部槽函数和公共方法 ---
    def set_diagram_model(self, loaded_diagram: FeynmanDiagram):
        """
        根据新加载的Diagram对象更新当前的diagram_model。
        方法：清空现有模型内容，然后将加载的元素逐一添加到现有模型中。
        """
        pass

    def _on_tool_mode_changed(self, mode: str):
        """当工具模式改变时，更新 MainController 内部状态。"""
        self._current_tool_mode = mode
        self.status_message.emit(f"当前模式: {mode.replace('_', ' ').title()}")
        self.clear_selection() # 切换模式时清空选择

    def _initialize_diagram_data(self):
        """
        初始化一些示例图数据或从文件加载。
        """
        # 示例：添加一些初始顶点和线条
        v1 = self.diagram_model.add_vertex(x=0, y=0, label=r"v^1\_")
        v2 = self.diagram_model.add_vertex(x=5, y=5, label=r"v^2", vertex_type=VertexType.HIGHER_ORDER)
        v3 = self.diagram_model.add_vertex(x=5, y=0, label=r"J/\psi")
        
        self.diagram_model.add_line(v_start=v1, v_end=v2, label="l1", line_type=FermionLine)
        self.diagram_model.add_line(v_start=v2, v_end=v3, label="l2", line_type=PhotonLine)
        self.picture_model()
        # 这里不需要 update_all_views()，因为 __init__ 的最后会调用

    def update_all_views(self, picture_model = False,
                            canvas_options: Optional[Dict[str, Any]] = None, 
                            vertex_options: Optional[Dict[str, Any]] = None, 
                            line_options: Optional[Dict[str, Any]] = None,
                            other_texts_options: Optional[Dict[str, Any]] = None
                        ):
        """
        强制所有视图重新绘制，并更新列表。
        当模型数据发生改变时，由 MainController 主动调用。
        """
        # 确保传入的字典不为 None，如果为 None 则使用空字典
        if picture_model:
            self.picture_model()
        canvas_opts = dict(canvas_options) if canvas_options is not None else {}
        if self.always_auto_scale:
            canvas_opts['auto_scale'] = True
        vertex_opts = vertex_options if vertex_options is not None else {}
        line_opts = line_options if line_options is not None else {}
        other_texts_options = other_texts_options if other_texts_options is not None else {}

        
        # 将这些字典解包为关键字参数，传递给对应的控制器方法
        self.canvas_controller.update_canvas(**canvas_opts)
        self.vertex_controller.update_vertex_list(**vertex_opts)
        self.line_controller.update_line_list(**line_opts)
        self.other_texts_controller.update_text_list(**other_texts_options)
        # 更新其他可能需要刷新的 UI 元素，例如属性面板等
        self.status_message.emit("视图已更新。")

    def update_canvas_only(self, canvas_options: Optional[Dict[str, Any]] = None):
        """
        仅更新画布视图（不刷新列表/文本面板）。
        用于拖动、平移、缩放等高频交互，避免 update_all_views 的额外 UI 开销；
        同时跳过导航栏范围更新，以减小重渲染开销。
        """
        canvas_opts = dict(canvas_options) if canvas_options else {}
        canvas_opts.setdefault('skip_navigation_bar', True)
        self.canvas_controller.update_canvas(**canvas_opts)


    def _handle_list_blank_clicked(self):
        """
        处理列表空白处被点击的信号，统一调用 select_item(None) 来清除所有选中。
        """
        cout("列表空白处被点击，清除所有选中。")
        self.select_item(None) # 统一调用 select_item 方法，传入 None 表示取消所有选中


    def select_item(self, item: [Vertex, Line, None], item_id: Optional[str] = None):
        """
        统一管理应用程序中的选中状态。
        由各个子控制器（如 VertexController, CanvasController）直接调用。
        :param item: 要选中的 Vertex 或 Line 对象，或 None 表示清除选中。
        :param item_id: 可选的选中项 ID，用于 label 高亮（如 vlabel:vertex_1、llabel:line_1）。
        """
        cout(f"\nMainController.select_item: 接收到项: {item}, 类型: {type(item)}, item_id: {item_id}")

        try:
            # 0. 更新 _current_selected_item_id（用于 label 高亮）
            self._current_selected_item_id = item_id if item_id else None

            # 1. 首先清除之前选中项的 is_selected 状态
            if self._current_selected_item is not None:
                cout(f"MainController: 清除旧选中项 {self._current_selected_item.id}.is_selected = False")
                self._current_selected_item.is_selected = False

            # 2. 更新 MainController 内部的当前选中项引用
            self._current_selected_item = item

            # 3. 如果有新选中项，设置其 is_selected 状态为 True
            if self._current_selected_item is not None:
                cout(f"MainController: 设置新选中项 {self._current_selected_item.id}.is_selected = True")
                self._current_selected_item.is_selected = True

                item_type_str = ''
                if isinstance(self._current_selected_item, Vertex):
                    item_type_str = '顶点'
                elif isinstance(self._current_selected_item, Line):
                    item_type_str = '线条'

                # self.status_message.emit(f"选中: {self._current_selected_item.id} ({item_type_str})")
                # print(f"选中: {self._current_selected_item.id} ({item_type_str})")
                cout(f"Current selected item (model ID): {self._current_selected_item.id}, is_selected: {self._current_selected_item.is_selected}")

            else:
                cout("MainController: 取消选中所有项。")
                self.status_message.emit("当前没有选中任何项。")

            # 4. 无论选中状态如何，统一通知所有相关视图控制器更新它们的UI显示
            # 这些更新会读取模型的 is_selected 状态来刷新 UI
            self.canvas_controller.update_canvas() # 更新画布
            # 调用子控制器的方法来更新列表视图的选中状态
            self.vertex_controller.set_selected_item_in_list(self._current_selected_item)
            self.line_controller.set_selected_item_in_list(self._current_selected_item) # 假设也有 line_controller

            self.print_all_selected_items() # 调试用

            return self._current_selected_item

        except Exception as e:
            cout(f"MainController: 选择项时发生错误: {e}")
            # 错误时尝试清除选中状态
            if self._current_selected_item is not None:
                self._current_selected_item.is_selected = False
                self._current_selected_item = None
            self.status_message.emit(f"错误：选择项失败 - {e}")
            self.canvas_controller.update_canvas()
            self.vertex_controller.set_selected_item_in_list(None)
            self.line_controller.set_selected_item_in_list(None)
            return None


        # # 通知画布刷新，确保选中状态在UI上正确显示
        # if self.canvas_widget:
        #     self.canvas_widget.repaint()

        # 通知属性面板更新（如果存在）
        # self.property_panel_controller.update_properties(item) # 示例

    def print_all_selected_items(self):
        """打印所有选中项。"""
        for v in self.diagram_model.vertices:
            if v.is_selected:
                cout(f"顶点: {v.id} is selected.")

        for l in self.diagram_model.lines:
            if l.is_selected:
                cout(f"线条: {l.id} is selected.")

    def clear_selection(self):
        """清空当前选中状态。"""
        self.select_item(None) # 调用通用方法清空

    def get_selected_item(self) -> [Vertex, Line, None]:
        """获取当前选中项。"""
        return self._current_selected_item

    def _is_text_edit_widget(self, obj) -> bool:
        """判断当前焦点是否在需保留按键的控件内（编辑框、列表等），若是则不应拦截 Delete/Backspace/方向键。"""
        w = obj
        while w is not None:
            if isinstance(w, (QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit, QComboBox, QListWidget)):
                return True
            try:
                w = w.parent()
            except Exception:
                break
        return False

    def eventFilter(self, obj, event):
        """拦截方向键、F2、Delete/Backspace。列表用 Page Up/Down 切换选中项。"""
        if event.type() != QEvent.Type.KeyPress:
            return False
        key = event.key()
        focus = QApplication.focusWidget()
        in_edit = focus is not None and self._is_text_edit_widget(focus)
        # 当选中 label 或 TextElement 时，方向键用于移动，即使焦点在列表上也需拦截
        item = self.get_selected_item()
        sel_id = getattr(self, '_current_selected_item_id', None)
        moveable_by_arrow = isinstance(item, TextElement) or (
            sel_id and (str(sel_id).startswith("vlabel:") or str(sel_id).startswith("llabel:"))
        )
        # 焦点在编辑控件内：Delete/F2 不拦截；方向键仅在无可移动项时不拦截
        if in_edit:
            if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                return False
            if key == Qt.Key.Key_F2:
                return False
            if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down) and not moveable_by_arrow:
                return False

        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.delete_selected_object()
            return True
        if key == Qt.Key.Key_F2:
            self.edit_item_properties(self.get_selected_item())
            return True
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self._handle_arrow_key(event)
            return True
        return False

    def _handle_arrow_key(self, event):
        """
        方向键精细控制：选中顶点时移动顶点；未选中或选中线条/文本时平移画布。
        移动顶点时：格点模式步长 1/2/1，非格点 0.1/0.01/0.25；平移画布始终用 0.1/0.01/0.25。
        """
        item = self.get_selected_item()
        mods = event.modifiers()
        # 仅移动顶点时，格点模式用格点步长；平移画布始终用原步长
        if isinstance(item, Vertex) and self.canvas_controller.only_allow_grid_points:
            if mods & Qt.KeyboardModifier.ShiftModifier:
                step = CANVAS_CONTROLLER_DEFAULTS.get("ARROW_STEP_GRID_LARGE", 2)
            else:
                step = CANVAS_CONTROLLER_DEFAULTS.get("ARROW_STEP_GRID", 1)
        else:
            if mods & Qt.KeyboardModifier.ControlModifier:
                step = CANVAS_CONTROLLER_DEFAULTS.get("ARROW_STEP_FINE", 0.01)
            elif mods & Qt.KeyboardModifier.ShiftModifier:
                step = CANVAS_CONTROLLER_DEFAULTS.get("ARROW_STEP_LARGE", 0.25)
            else:
                step = CANVAS_CONTROLLER_DEFAULTS.get("ARROW_STEP", 0.1)
        key = event.key()
        dx = {-1: -step, 1: step}.get((key == Qt.Key.Key_Right) - (key == Qt.Key.Key_Left), 0)
        dy = {-1: -step, 1: step}.get((key == Qt.Key.Key_Up) - (key == Qt.Key.Key_Down), 0)
        if dx == 0 and dy == 0:
            return

        # 选中顶点/线条 label 时，用方向键移动 label_offset（优先于顶点移动）
        sel_id = getattr(self, '_current_selected_item_id', None)
        if sel_id and (sel_id.startswith("vlabel:") or sel_id.startswith("llabel:")):
            if self.canvas_controller.apply_label_offset_move(sel_id, dx, dy):
                self.update_all_views(canvas_options={
                    'target_xlim': self.main_window.canvas_widget_instance.get_axes().get_xlim(),
                    'target_ylim': self.main_window.canvas_widget_instance.get_axes().get_ylim(),
                })
                return
        if isinstance(item, Vertex):
            self.canvas_controller.apply_vertex_move(item, item.x + dx, item.y + dy)
            self.vertex_controller.update_vertex_list()
            opts = self.canvas_controller.get_canvas_options_for_object_at_position(item)
            self.update_all_views(canvas_options=opts)
            return
        if isinstance(item, TextElement):
            # 其余文本：用方向键移动位置
            item.x += dx
            item.y += dy
            self.other_texts_controller.update_text_list()
            opts = self.canvas_controller.get_canvas_options_for_object_at_position(item)
            self.update_all_views(canvas_options=opts)
            return
        # 无选中或选中线条：平移画布
        ax = self.main_window.canvas_widget_instance.get_axes()
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        self.update_all_views(canvas_options={
            "target_xlim": (xlim[0] + dx, xlim[1] + dx),
            "target_ylim": (ylim[0] + dy, ylim[1] + dy),
        })

        
    def _handle_object_moved_on_canvas(self, item_id: str, new_pos: QPointF):
        """处理画布上对象被拖动移动的事件。"""
        obj = self.diagram_model.get_vertex_by_id(item_id) # 只有顶点可以被拖动移动
        if isinstance(obj, Vertex):
            self.diagram_model.update_vertex_properties(obj, x=new_pos.x(), y=new_pos.y()) # 只更新位置
            self.status_message.emit(f"移动了顶点 {obj.id} 到 ({new_pos.x():.2f}, {new_pos.y():.2f})")
            self.update_all_views() # 移动后强制更新视图


    def _handle_list_line_selection(self, line_id: str):
        """处理线条列表中的选择事件。"""
        line = self.diagram_model.get_line_by_id(line_id)
        self.select_item(line)

    def _handle_list_line_double_clicked(self, line_id: str):
        """处理线条列表中的双击事件。"""
        line = self.diagram_model.get_line_by_id(line_id)
        if line:
            self.edit_item_properties(line)


    # --- 公共操作方法 (由其他控制器或 UI 触发) ---

    def start_add_vertex_process(self):
        """启动添加顶点的流程。"""
        self.add_vertex_at_coords()
        
    def add_vertex_at_coords(self):
        dialog = AddVertexDialog(diagram = self.diagram_model, parent=self.main_window)
        # dialog.set_position(x, y) # 预设点击的位置
        if dialog.exec() == QDialog.Accepted:
            x, y, label = dialog.get_coordinates()
            if x is not None and y is not None:
                # 先检查是否已有相同坐标的顶点
                for vertex in self.diagram_model.vertices:
                    if abs(vertex.x - x) < 1e-6 and abs(vertex.y - y) < 1e-6:
                        # 发现重复点，弹提示并返回
                        self.status_message.emit(f"已存在坐标为({x:.2f}, {y:.2f})的顶点，不能重复添加。")
                        MsgBox.warning(self.main_window, "添加顶点错误",
                                            f"已存在坐标为({x:.2f}, {y:.2f})的顶点，不能重复添加。")
                        return
                
                try:
                    new_vertex = self.diagram_model.add_vertex(
                        x=x,
                        y=y,
                        label=label,
                    )
                    cout3(f"已添加顶点: {new_vertex.id} 在 ({new_vertex.x:.2f}, {new_vertex.y:.2f})")
                    self.status_message.emit(f"已添加顶点: {new_vertex.id} 在 ({new_vertex.x:.2f}, {new_vertex.y:.2f})")
                    self.update_all_views(canvas_options={'auto_scale': True}) # 添加后更新所有视图
                    self.select_item(new_vertex)  # 添加后选中新顶点
                    self.picture_model()
                except ValueError as e:
                    self.status_message.emit(f"添加顶点失败: {e}")
                    MsgBox.warning(self.main_window, "添加顶点错误", f"添加顶点失败: {e}")
            else:
                self.status_message.emit("顶点添加已取消。")
        else:
            self.status_message.emit("顶点添加已取消。")



    def start_add_line_process(self):
        """
        启动添加线条的流程，委托给 CanvasController 处理鼠标事件。
        """
        self.add_line_between_vertices()
        # CanvasController 会收集点击的顶点，然后通过 line_creation_completed 信号调用 MainController 的 add_line_between_vertices

    def add_line_between_vertices(self, initial_start_vertex_id: str = None):
            """
            弹出对话框，允许用户选择两个顶点并添加一条线条。
            
            Args:
                initial_start_vertex_id (str, optional): 如果提供，将预设对话框中的起始顶点。
            """
            dialog = AddLineDialog(
                vertices_data=self.diagram_model.vertices,
                parent=self.main_window,
                initial_start_vertex_id=initial_start_vertex_id
            )

            if dialog.exec() == QDialog.Accepted:
                line_info = dialog.get_line_data()
                if line_info:
                    final_v_start = line_info['v_start']
                    final_v_end = line_info['v_end']
                    
                    # `AddLineDialog` 的 `get_line_data()` 方法已经处理了
                    # `start_vertex == end_vertex` 的警告，并返回了 None。
                    # 所以在这里我们只需检查 `line_info` 是否为 None 即可。

                    try:
                        new_line = self.diagram_model.add_line(
                            v_start=final_v_start,
                            v_end=final_v_end,
                            label=line_info.get('label', ''),
                            line_type=line_info['line_type'],
                            loop=line_info.get('loop', False),
                        )
                        self.status_message.emit(f"已添加线条: {new_line.id} 连接 {final_v_start.id} 和 {final_v_end.id}")
                        self.update_all_views()
                        self.select_item(new_line)
                        self.picture_model()
                    except ValueError as e:
                        self.status_message.emit(f"添加线条失败: {e}")
                        MsgBox.warning(self.main_window, "添加线条错误", f"添加线条失败: {e}")
                        cout(f"添加线条失败: {e}")
                    except Exception as e:
                        self.status_message.emit(f"添加线条时发生未知错误: {e}")
                        MsgBox.critical(self.main_window, "添加线条错误", f"添加线条时发生未知错误: {e}")
                else:
                    # 当 get_line_data() 返回 None 时，表示用户输入无效
                    cout("线条添加已取消。")
            else:
                # 当用户点击取消按钮时
                cout("线条添加已取消。")
                
            self.canvas_controller.reset_line_creation_state()


    def _get_pre_selected_or_from_ui(self, param_item, expected_type):
        """从参数或当前选中项获取预选对象。"""
        if param_item is not None and isinstance(param_item, expected_type):
            return param_item
        item = self.get_selected_item()
        return item if isinstance(item, expected_type) else None

    def delete_selected_vertex(self, vertex_to_delete: Optional[Vertex] = None):
        """弹出对话框让用户选择或确认要删除的顶点，并执行删除操作。"""
        if not self.diagram_model.vertices:
            MsgBox.information(self.main_window, self.tr("没有顶点"), self.tr("图中目前没有可供删除的顶点。"))
            self.status_message.emit("删除顶点失败：图中没有顶点。")
            return
        pre_selected = self._get_pre_selected_or_from_ui(vertex_to_delete, Vertex)
        dialog = DeleteVertexDialog(self.diagram_model, vertex_to_delete=pre_selected, parent=self.main_window)
        if dialog.exec() == QDialog.Accepted:
            selected_id = dialog.get_selected_vertex_id()
            if selected_id:
                obj = self.diagram_model.get_vertex_by_id(selected_id)
                label = obj.label if obj else selected_id
                try:
                    if self.diagram_model.delete_vertex(selected_id):
                        self.status_message.emit(f"已删除顶点: {label} (ID: {selected_id})。")
                        self.picture_model()
                        self.update_all_views(canvas_options={'auto_scale': True})
                        self.clear_selection()
                    else:
                        MsgBox.warning(self.main_window, "删除失败", f"无法删除顶点 '{label}' (ID: {selected_id})。")
                        self.status_message.emit(f"顶点 '{label}' 删除失败。")
                except Exception as e:
                    self.status_message.emit(f"删除顶点时发生未知错误: {e}")
                    MsgBox.critical(self.main_window, "删除顶点错误", str(e))
            else:
                MsgBox.warning(self.main_window, self.tr("删除失败"), self.tr("未选择任何顶点。"))
        else:
            self.status_message.emit("顶点删除操作已取消。")

    def delete_selected_line(self, line_to_delete: Optional[Line] = None):
        """弹出对话框让用户选择或确认要删除的线条，并执行删除操作。"""
        if not self.diagram_model.lines:
            MsgBox.information(self.main_window, self.tr("没有线条"), self.tr("图中目前没有可供删除的线条。"))
            self.status_message.emit("删除线条失败：图中没有线条。")
            return
        pre_selected = self._get_pre_selected_or_from_ui(line_to_delete, Line)
        dialog = DeleteLineDialog(self.diagram_model, line_to_delete=pre_selected, parent=self.main_window)
        if dialog.exec() == QDialog.Accepted:
            selected_line = dialog.get_selected_line()
            if selected_line:
                try:
                    if self.diagram_model.delete_line(selected_line.id):
                        self.status_message.emit(f"线条 '{selected_line.id}' 已删除。")
                        self.update_all_views()
                        self.clear_selection()
                    else:
                        MsgBox.warning(self.main_window, "删除失败", f"无法删除线条 '{selected_line.id}'。")
                except Exception as e:
                    self.status_message.emit(f"删除线条时发生未知错误: {e}")
                    MsgBox.critical(self.main_window, "删除线条错误", str(e))
            else:
                MsgBox.warning(self.main_window, self.tr("删除失败"), self.tr("未选择任何线条。"))
        else:
            self.status_message.emit("删除线条操作已取消。")


    def delete_selected_object(self):
        """删除当前选中的对象（顶点、线条或其余文本），弹出确认框。"""
        item = self.get_selected_item()
        if isinstance(item, Vertex):
            self.delete_selected_vertex(item)
        elif isinstance(item, Line):
            self.delete_selected_line(item)
        elif isinstance(item, TextElement):
            self.other_texts_controller._on_request_delete_text(item)
        else:
            self.status_message.emit("请先选中要删除的顶点、线条或文本。")

    # --- 文件操作 ---
    def save_diagram_to_file(self):
        """保存当前图到文件。支持 .pdf, .png, .jpg 格式。"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.main_window, # Parent widget for the dialog
            "保存费曼图图像",  # Dialog title
            "",               # Default directory (empty means current)
            "PDF Files (*.pdf);;PNG Images (*.png);;JPEG Images (*.jpg);;SVG Images (*.svg);;All Files (*)" 
        )
        
        if not file_path:
            self.status_message.emit("保存操作已取消。")
            return
        # return
        try:
            cout(f"文件路径: {file_path}")
            # 根据选择的过滤器确定扩展名
            extension_mapping = {
                "PDF Files (*.pdf)": ".pdf",
                "PNG Images (*.png)": ".png",
                "JPEG Images (*.jpg)": ".jpg",
                "SVG Images (*.svg)": ".svg",
            }
            # 默认为 .png，以防用户选择 "All Files (*)" 且未输入扩展名
            extension = extension_mapping.get(selected_filter, ".png") 

            # 规范化文件路径：如果文件路径没有以选定格式的扩展名结尾，则添加它
            if not file_path.lower().endswith(extension.lower()):
                # 如果用户输入了其他图像扩展名（如.jpeg），则使用用户输入的
                # 否则，使用默认或选择的扩展名
                input_ext = os.path.splitext(file_path)[1].lower()
                if input_ext in ['.pdf', '.png', '.jpg']:
                    # 用户输入了有效图像扩展名，就用它的
                    pass 
                else:
                    # 否则，补充我们推荐的扩展名
                    file_path = f"{file_path}{extension}"
            
            # 确保目录存在
            # os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            # return
            # 获取画布后端并保存图像
            backend = self.canvas_controller.get_backend()
            if backend is None:
                raise ValueError("画布后端未初始化，无法保存图像。")
            # return
            # Matplotlib 的 savefig 方法会根据文件扩展名自动处理图像格式
            # 使用后端设置中的 savefig.dpi，若未设置则默认 300
            import matplotlib.pyplot as plt
            save_dpi = plt.rcParams.get('savefig.dpi', 300)
            if isinstance(save_dpi, str) and save_dpi.lower() == 'figure':
                save_dpi = plt.rcParams.get('figure.dpi', 100)
            backend.savefig(file_path,
                             bbox_inches='tight', pad_inches=0.02, dpi=save_dpi
                             )
            cout(f"图像已成功保存到: {file_path}")
            # self.status_message.emit(f"图像已成功保存到: {file_path}")

        except Exception as e:
            MsgBox.critical(
                self.main_window,
                "保存失败",
                f"保存图像时发生错误：\n{str(e)}\n\n请检查文件路径和权限。"
            )
            self.status_message.emit(f"保存失败: {str(e)}")

    def clear_diagram(self):
        """
        清空图表，使用 PySide6 自带的 QMessageBox 进行二次确认。
        """
        reply = MsgBox.question(
            self.main_window, # 父窗口
            "再次确认清空图表",       # 弹窗标题
            "再次确认：您确定要清空当前图表吗？", # 弹窗消息
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, # 确认和取消按钮
            QMessageBox.StandardButton.No # 默认选中“否”按钮
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.diagram_model.clear_diagram() # 假设 FeynmanDiagram 有 clear_diagram 方法
                self.update_all_views()
                self.clear_selection()
                self.status_message.emit("图表已清空。")
            except Exception as e:
                self.status_message.emit(f"清空图表失败: {e}")
                MsgBox.critical(self.main_window, "清空图表错误", f"清空图表失败: {e}")
        else:
            self.status_message.emit("清空图表操作已取消。")

    def save_diagram_from_toolbox(self):
        # MsgBox.information(self.main_window, self.tr("提示"), self.tr("save_diagram_from_toolbox"))
        # exit()
        self.save_diagram_to_file()

    def save_diagram_from_navigation_bar(self):
        # QMessageBox().information(self.main_window, "提示", "save_diagram_from_navigation_bar")
        self.save_diagram_to_file()
    # --- 其他辅助方法 ---
    # 你可能还需要实现其他更复杂的交互，如多选，复制粘贴等。


    def edit_item_properties(self, item: Union[Vertex, Line, TextElement, None]):
        """编辑顶点、线条或其余文本的属性。"""
        if item is None:
            return
        if isinstance(item, Vertex):
            self.vertex_controller._on_edit_vertex_requested_from_list(item)
        elif isinstance(item, Line):
            self.line_controller._on_request_edit_line(item)
        elif isinstance(item, TextElement):
            self.other_texts_controller._on_request_edit_text(item)    
    
    def picture_model(self):
        cout("Model pictured.")
        self.toolbox_controller._save_current_diagram_state()
        self.toolbox_controller._update_undo_redo_button_states()

    def _update_canvas_range_on_navigation_bar(self):
        # print("Updating navigation bar ui for canvas.")
        (xmin, xmax), (ymin, ymax) = self.canvas_controller._canvas_instance.get_axes_limits()
        self.navigation_bar_controller.navigation_bar_widget.update_plot_limits(xmin, xmax, ymin, ymax)
        # self.navigation_bar_controller._on_canvas_set_range_ui(xmin, xmax, ymin, ymax)