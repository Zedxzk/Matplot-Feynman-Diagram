# feynplot_GUI/feynplot_gui/controllers/main_controller.py

from debug_utils import cout, cout3
from PySide6.QtCore import QObject, Signal, QPointF
from PySide6.QtWidgets import QMessageBox, QDialog, QFileDialog

# 导入所有控制器
from .canvas_controller import CanvasController
from .navigation_bar_controller import NavigationBarController
from .toolbox_controller import ToolboxController
from .vertex_controller import VertexController
from .line_controller import LineController

# 导入核心模型类和其组成部分
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import Line, FermionLine, PhotonLine, GluonLine, LineStyle # 确保所有需要的线条类和样式被导入

# 导入主窗口 (方便类型提示和访问其子组件实例)
from feynplot_gui.widgets.main_window import MainWindow
# 导入对话框，因为 MainController 现在负责它们的创建和数据显示
from feynplot_gui.dialogs.add_vertex_dialog import AddVertexDialog
from feynplot_gui.dialogs.edit_vertex_dialog import EditVertexDialog
from feynplot_gui.dialogs.add_line_dialog import AddLineDialog
from feynplot_gui.dialogs.edit_line_dialog import EditLineDialog
from feynplot_gui.dialogs.delete_vertex_dialog import DeleteVertexDialog
from feynplot_gui.dialogs.delete_line_dialog import DeleteLineDialog

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
        # 跟踪当前工具模式，MainController负责管理并转发给CanvasController
        self._current_tool_mode = "select" # 默认选择模式

        # 实例化所有子控制器，并传递必要的依赖（模型、UI组件实例、MainController自身）
        # 注意：这里我们使用 main_window 暴露的 'xxx_instance' 属性
        self.canvas_controller = CanvasController(
            diagram_model=self.diagram_model,
            canvas_widget=self.main_window.canvas_widget_instance,
            main_controller=self
        )
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

        # 初始加载或设置一些默认数据
        self._initialize_diagram_data()

        # 连接所有 UI 信号到控制器槽函数
        self._link_controllers_signals()

        # 连接 MainController 自身的信号到主窗口的状态栏
        # self.status_message.connect(self.main_window.show_status_message)

        # 初始更新所有视图
        self.update_all_views()
        self.status_message.emit("应用程序已启动。")


    def _link_controllers_signals(self):
        """连接所有UI组件发出的信号到对应的控制器槽函数。"""

        # --- CanvasWidget 信号连接 ---
        # CanvasWidget 应该报告用户点击或选择事件的原始 Matplotlib 坐标和对象ID
        # 这些信号现在直接连接到 MainController 的处理方法
        # self.main_window.canvas_widget_instance.canvas_clicked.connect(self._handle_canvas_click)
        # self.main_window.canvas_widget_instance.object_selected.connect(self._handle_object_selected_on_canvas)
        # self.main_window.canvas_widget_instance.object_double_clicked.connect(self._handle_object_double_clicked_on_canvas)
        # self.main_window.canvas_widget_instance.object_moved.connect(self._handle_object_moved_on_canvas)
        # self.main_window.canvas_widget_instance.selection_cleared.connect(self.clear_selection)
        # # CanvasController 需要在添加线条模式下通知 MainController 完成线条添加
        # self.canvas_controller.line_creation_completed.connect(self.add_line_between_vertices)


        # # --- ToolboxWidget 信号连接 ---
        # # ToolboxController 现在负责管理模式切换，并发出 mode_changed 信号给 MainController
        # self.toolbox_controller.mode_changed.connect(self._on_tool_mode_changed) # 内部更新 MainController 的模式
        # self.toolbox_controller.mode_changed.connect(self.canvas_controller.set_mode) # 更新 CanvasController 的模式
        
        # 将 ToolboxWidget 的操作信号直接连接到 MainController 的方法
        # 假设 ToolboxWidget 已经有这些信号
        self.main_window.toolbox_widget_instance.add_vertex_requested.connect(self.start_add_vertex_process)
        self.main_window.toolbox_widget_instance.add_line_requested.connect(self.start_add_line_process)
        self.main_window.toolbox_widget_instance.delete_vertex_requested.connect(self.delete_selected_vertex)
        self.main_window.toolbox_widget_instance.delete_line_requested.connect(self.delete_selected_line)
        self.main_window.toolbox_widget_instance.save_diagram_requested.connect(self.save_diagram_to_file)
        # self.main_window.toolbox_widget_instance.load_diagram_requested.connect(self.load_diagram_from_file)
        self.main_window.toolbox_widget_instance.undo_action_requested.connect(self.undo)
        self.main_window.toolbox_widget_instance.redo_action_requested.connect(self.redo)


        # --- NavigationBarWidget 信号连接 ---
        self.main_window.navigation_bar_widget_instance.add_vertex_button_clicked.connect(self.start_add_vertex_process)
        self.main_window.navigation_bar_widget_instance.add_line_button_clicked.connect(self.start_add_line_process)
        self.main_window.navigation_bar_widget_instance.save_project_action_triggered.connect(self.save_diagram_to_file)
        self.main_window.navigation_bar_widget_instance.load_project_action_triggered.connect(self.load_diagram_from_file)
        # self.main_window.navigation_bar_widget_instance.clear_diagram_action_triggered.connect(self.clear_diagram)
        
        # 对象菜单的通用编辑和删除信号 (由 NavigationBarWidget 发出)
        # self.main_window.navigation_bar_widget_instance.edit_selected_object_triggered.connect(self.edit_selected_object_properties)
        # self.main_window.navigation_bar_widget_instance.delete_selected_object_triggered.connect(self.delete_selected_object)


        # --- VertexListWidget 信号连接 ---
        self.main_window.vertex_list_widget_instance.vertex_selected.connect(self._handle_list_vertex_selection)
        self.main_window.vertex_list_widget_instance.vertex_double_clicked.connect(self._handle_list_vertex_double_clicked)

        # --- LineListWidget 信号连接 ---
        self.main_window.line_list_widget_instance.line_selected.connect(self._handle_list_line_selection)
        self.main_window.line_list_widget_instance.line_double_clicked.connect(self._handle_list_line_double_clicked)

        # --- MainController 自身信号的连接 ---
        # 当选中项改变时，通知其他需要更新的UI组件和控制器
        # self.selection_changed.connect(self.canvas_controller.set_selected_object) # CanvasWidget 根据 ID 和 Type 更新高亮
        self.selection_changed.connect(self.vertex_controller.set_selected_item_in_list) # 列表选中状态
        self.selection_changed.connect(self.line_controller.set_selected_item_in_list)  # 列表选中状态
        self.selection_changed.connect(self.navigation_bar_controller.update_object_menu_status) # 更新对象菜单的启用状态
        # self.selection_changed.connect(self.toolbox_controller.update_delete_buttons_status) # 如果 toolbox_controller 有这个方法


    # --- MainController 内部槽函数和公共方法 ---

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
        v1 = self.diagram_model.add_vertex(x=0, y=0, label="v1")
        v2 = self.diagram_model.add_vertex(x=5, y=5, label="v2", vertex_type=VertexType.HIGHER_ORDER)
        v3 = self.diagram_model.add_vertex(x=5, y=0, label="v3")
        
        self.diagram_model.add_line(v_start=v1, v_end=v2, label="l1", line_type=FermionLine)
        self.diagram_model.add_line(v_start=v2, v_end=v3, label="l2", line_type=PhotonLine)
        
        # 这里不需要 update_all_views()，因为 __init__ 的最后会调用

    def update_all_views(self):
        """
        强制所有视图重新绘制，并更新列表。
        当模型数据发生改变时，由 MainController 主动调用。
        """
        self.canvas_controller.update_canvas()
        self.vertex_controller.update_vertex_list()
        self.line_controller.update_line_list()
        # 更新其他可能需要刷新的 UI 元素，例如属性面板等
        self.status_message.emit("视图已更新。")


    def select_item(self, item: [Vertex, Line, None]):
        """
        设置当前选中项并通知所有订阅者。
        参数 item 可以是 Vertex 实例，Line 实例，或 None (表示清空选择)。
        """
        if self._current_selected_item is item: # 如果选中项没有变化，则不触发更新
            return

        # 清除旧选中项的 is_selected 状态 (假定 Vertex/Line 对象有 is_selected 属性)
        if self._current_selected_item:
            self._current_selected_item.is_selected = False

        self._current_selected_item = item

        # 设置新选中项的 is_selected 状态
        if self._current_selected_item:
            self._current_selected_item.is_selected = True
            self.selection_changed.emit(self._current_selected_item)
            self.status_message.emit(f"选中: {self._current_selected_item.id} ({'顶点' if isinstance(self._current_selected_item, Vertex) else '线条'})")
        else:
            self.selection_changed.emit(None) # 广播清空选择
            self.status_message.emit("选中项: 无")

        # 强制 CanvasWidget 重绘以更新高亮状态 (由 canvas_controller.set_selected_object 间接触发)
        # self.canvas_controller.update_canvas() # 这一行可以省略，因为 set_selected_object 会导致 canvas 重新绘制

    def clear_selection(self):
        """清空当前选中状态。"""
        self.select_item(None) # 调用通用方法清空

    def get_selected_item(self) -> [Vertex, Line, None]:
        """获取当前选中项。"""
        return self._current_selected_item

    # --- CanvasWidget 报告的交互事件处理 ---
    def _handle_canvas_click(self, pos: QPointF):
        """处理画布点击事件，根据当前模式添加对象或进行选择。"""
        if self._current_tool_mode == "add_vertex":
            self.add_vertex_at_coords(pos.x(), pos.y())
        elif self._current_tool_mode == "add_line":
            # 如果是添加线条模式，将点击事件转发给 CanvasController 处理
            # CanvasController 会负责收集两个顶点，然后通过 line_creation_completed 信号通知 MainController
            self.canvas_controller.handle_add_line_click(pos)
        elif self._current_tool_mode == "select":
            # 选择模式下，CanvasWidget 应该已经处理了对象选择，
            # 并发出了 object_selected 或 selection_cleared 信号，这里不需要重复逻辑。
            pass # 已经被 canvas_widget.object_selected 信号处理

    def _handle_object_selected_on_canvas(self, item_id: str, item_type: str):
        """
        处理画布上对象被选中信号。
        item_id: 选中的对象ID
        item_type: "vertex" 或 "line"
        """
        if item_type == "vertex":
            obj = self.diagram_model.get_vertex_by_id(item_id)
        elif item_type == "line":
            obj = self.diagram_model.get_line_by_id(item_id)
        else:
            obj = None
        self.select_item(obj) # 统一通过 select_item 方法设置选中项

    def _handle_object_double_clicked_on_canvas(self, item_id: str, item_type: str):
        """处理画布上对象双击事件，通常用于编辑属性。"""
        self.status_message.emit(f"双击了 {item_type} ID: {item_id}")
        # 获取双击的对象
        if item_type == "vertex":
            obj = self.diagram_model.get_vertex_by_id(item_id)
        elif item_type == "line":
            obj = self.diagram_model.get_line_by_id(item_id)
        else:
            obj = None
        
        if obj:
            self.edit_item_properties(obj) # 调用编辑方法
        
    def _handle_object_moved_on_canvas(self, item_id: str, new_pos: QPointF):
        """处理画布上对象被拖动移动的事件。"""
        obj = self.diagram_model.get_vertex_by_id(item_id) # 只有顶点可以被拖动移动
        if isinstance(obj, Vertex):
            self.diagram_model.update_vertex_properties(obj, x=new_pos.x(), y=new_pos.y()) # 只更新位置
            self.status_message.emit(f"移动了顶点 {obj.id} 到 ({new_pos.x():.2f}, {new_pos.y():.2f})")
            self.update_all_views() # 移动后强制更新视图

    # --- 列表视图信号处理 ---
    def _handle_list_vertex_selection(self, vertex_id: str):
        """处理顶点列表中的选择事件。"""
        vertex = self.diagram_model.get_vertex_by_id(vertex_id)
        self.select_item(vertex)

    def _handle_list_vertex_double_clicked(self, vertex_id: str):
        """处理顶点列表中的双击事件。"""
        vertex = self.diagram_model.get_vertex_by_id(vertex_id)
        if vertex:
            self.edit_item_properties(vertex)

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
        # parent_window = self.main_window if 
        # self.toolbox_controller.set_add_vertex_mode() # 切换工具箱模式
        # self.status_message.emit("请在画布上点击以添加顶点。")

    def add_vertex_at_coords(self):
        dialog = AddVertexDialog(parent=self.main_window)
        # dialog.set_position(x, y) # 预设点击的位置
        if dialog.exec() == QDialog.Accepted:
            x, y, label = dialog.get_coordinates()
            if x is not None and y is not None:
                # 先检查是否已有相同坐标的顶点
                for vertex in self.diagram_model.vertices:
                    if abs(vertex.x - x) < 1e-6 and abs(vertex.y - y) < 1e-6:
                        # 发现重复点，弹提示并返回
                        self.status_message.emit(f"已存在坐标为({x:.2f}, {y:.2f})的顶点，不能重复添加。")
                        QMessageBox.warning(self.main_window, "添加顶点错误",
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
                    self.update_all_views()  # 添加后更新所有视图
                    self.select_item(new_vertex)  # 添加后选中新顶点
                except ValueError as e:
                    self.status_message.emit(f"添加顶点失败: {e}")
                    QMessageBox.warning(self.main_window, "添加顶点错误", f"添加顶点失败: {e}")
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

    def add_line_between_vertices(self):
        dialog = AddLineDialog(self.diagram_model.vertices, parent=self.main_window)
        if dialog.exec() == QDialog.Accepted:
            line_info = dialog.get_line_data()
            if line_info:
                # 再次确认顶点是否被用户修改
                final_v_start = line_info['v_start']
                final_v_end = line_info['v_end']
                if final_v_start == final_v_end:
                    QMessageBox.warning(self.main_window, "输入错误", "起始顶点和结束顶点不能相同！")
                    self.status_message.emit("线条添加失败: 起始顶点和结束顶点相同。")
                    return
                try:
                    # 默认使用 FermionLine，可以扩展为选择线条类型
                    new_line = self.diagram_model.add_line(
                        v_start=final_v_start, 
                        v_end=final_v_end, 
                        label=line_info.get('label', ''), # 确保有 label 字段
                        line_type=line_info['line_type']
                    )
                    self.status_message.emit(f"已添加线条: {new_line.id} 连接 {final_v_start.id} 和 {final_v_end.id}")
                    self.update_all_views() # 添加后更新所有视图
                    self.select_item(new_line) # 添加后选中新线条
                except ValueError as e:
                    self.status_message.emit(f"添加线条失败: {e}")
                    QMessageBox.warning(self.main_window, "添加线条错误", f"添加线条失败: {e}")
                except Exception as e:
                    self.status_message.emit(f"添加线条时发生未知错误: {e}")
                    QMessageBox.critical(self.main_window, "添加线条错误", f"添加线条时发生未知错误: {e}")
            else:
                self.status_message.emit("线条添加已取消。")
        else:
            self.status_message.emit("线条添加已取消。")
        
        # self.toolbox_controller.set_select_mode() # 无论是否添加成功，都切换回选择模式
        self.canvas_controller.reset_line_creation_state() # 清除 CanvasController 中的临时线条创建状态


    def delete_selected_vertex(self):
        """
        弹出对话框让用户选择要删除的顶点，并执行删除操作。
        此方法从工具箱或其他UI触发。
        """
        # 1. 实例化删除顶点对话框，并传入当前图模型
        dialog = DeleteVertexDialog(self.diagram_model, parent=self.main_window)

        # 2. 检查图中是否有顶点可供删除。如果没有，直接提示并返回。
        if not self.diagram_model.vertices:
            QMessageBox.information(self.main_window, "没有顶点", "图中目前没有可供删除的顶点。")
            self.status_message.emit("删除顶点失败：图中没有顶点。")
            return

        # 3. 显示对话框并等待用户交互
        if dialog.exec() == QDialog.Accepted:
            # 4. 如果用户点击了“确定”，获取用户选择的顶点ID
            selected_vertex_id = dialog.get_selected_vertex_id()
            
            if selected_vertex_id:
                # 5. 再次获取选中顶点的对象，用于在消息中显示其标签
                # 这步是可选的，但可以提供更友好的用户反馈
                selected_vertex_obj = self.diagram_model.get_vertex_by_id(selected_vertex_id)
                vertex_label = selected_vertex_obj.label if selected_vertex_obj else selected_vertex_id

                # 6. 调用模型层的方法删除顶点
                try:
                    # diagram_model.delete_vertex 会同时处理关联边的删除
                    if self.diagram_model.delete_vertex(selected_vertex_id):
                        # 如果你有 cout3 函数，可以在这里使用
                        # cout3(f"已删除顶点: {selected_vertex_id}（标签: {vertex_label}）")
                        QMessageBox.information(self.main_window, "删除成功", 
                                                f"顶点 '{vertex_label}' (ID: {selected_vertex_id}) 及其关联线条已成功删除。")
                        self.status_message.emit(f"已删除顶点: {vertex_label} (ID: {selected_vertex_id})。")
                        self.update_all_views() # 删除后刷新视图
                        self.clear_selection() # 删除后清除当前选择
                    else:
                        # 理论上，如果 get_selected_vertex_id 返回了ID，delete_vertex 应该成功
                        # 但为了健壮性，这里保留一个失败提示
                        QMessageBox.warning(self.main_window, "删除失败", 
                                            f"无法删除顶点 '{vertex_label}' (ID: {selected_vertex_id})。")
                        self.status_message.emit(f"顶点 '{vertex_label}' (ID: {selected_vertex_id}) 删除失败。")
                except Exception as e:
                    # 捕获模型层可能抛出的其他异常
                    self.status_message.emit(f"删除顶点时发生未知错误: {e}")
                    QMessageBox.critical(self.main_window, "删除顶点错误", f"删除顶点时发生未知错误: {e}")
            else:
                # 用户点击了“确定”，但可能没有选择任何顶点 (理论上不应该发生，但以防万一)
                QMessageBox.warning(self.main_window, "删除失败", "未选择任何顶点。")
                self.status_message.emit("删除顶点操作：未选择顶点。")
        else:
            # 7. 如果用户点击了“取消”
            self.status_message.emit("顶点删除操作已取消。")


    # --- 新增的 delete_selected_line 方法 ---
    def delete_selected_line(self):
        """
        弹出对话框让用户选择要删除的线条，并执行删除操作。
        """
        # 1. 实例化删除线条对话框，并传入当前图模型
        dialog = DeleteLineDialog(self.diagram_model, parent=self.main_window)

        # 2. 检查图中是否有线条可供删除。如果没有，直接提示并返回。
        if not self.diagram_model.lines:
            QMessageBox.information(self.main_window, "没有线条", "图中目前没有可供删除的线条。")
            self.status_message.emit("删除线条失败：图中没有线条。")
            return

        # 3. 显示对话框并等待用户交互
        if dialog.exec() == QDialog.Accepted:
            # 4. 如果用户点击了“确定”，获取用户选择的线条对象
            selected_line = dialog.get_selected_line()
            
            if selected_line:
                # 5. 调用模型层的方法删除线条
                try:
                    if self.diagram_model.delete_line(selected_line.id):
                        QMessageBox.information(self.main_window, "删除成功", f"线条 '{selected_line.id}' 已成功删除。")
                        self.status_message.emit(f"线条 '{selected_line.id}' 已删除。")
                        self.update_all_views() # 删除后更新所有视图
                        self.clear_selection() # 删除后清除选中状态，防止选中已删除的对象
                    else:
                        # 理论上，如果 get_selected_line 返回了对象，delete_line 应该成功
                        # 但为了健壮性，这里保留一个失败提示
                        QMessageBox.warning(self.main_window, "删除失败", f"无法删除线条 '{selected_line.id}'。")
                        self.status_message.emit(f"线条 '{selected_line.id}' 删除失败。")
                except Exception as e:
                    # 捕获模型层可能抛出的其他异常
                    self.status_message.emit(f"删除线条时发生未知错误: {e}")
                    QMessageBox.critical(self.main_window, "删除线条错误", f"删除线条时发生未知错误: {e}")
            else:
                # 用户点击了“确定”，但下拉框中可能没有可选择的线条（虽然我们前面已经检查过）
                # 或者 get_selected_line 返回了 None
                QMessageBox.warning(self.main_window, "删除失败", "未选择任何线条。")
                self.status_message.emit("删除线条操作：未选择线条。")
        else:
            # 6. 如果用户点击了“取消”
            self.status_message.emit("删除线条操作已取消。")


    def delete_selected_object(self):
        """从导航栏通用删除按钮触发，删除当前选中的对象（顶点或线条）。"""
        # item = self.get_selected_item()
        # if isinstance(item, Vertex):
        #     self.delete_selected_vertex() # 调用专门删除顶点的方法
        # elif isinstance(item, Line):
        #     self.delete_selected_line() # 调用专门删除线条的方法
        # else:
        #     self.status_message.emit("没有选中的对象可以删除。")
        #     QMessageBox.information(self.main_window, "提示", "没有选中的对象可以删除。")
        pass

    def edit_item_properties(self, item: [Vertex, Line]):
        """
        打开属性编辑器来编辑选中项的属性。
        由双击事件或导航栏“编辑”菜单触发。
        """
        if item is None:
            self.status_message.emit("没有选中的对象可以编辑。")
            QMessageBox.information(self.main_window, "提示", "没有选中的对象可以编辑。")
            return
        
        if isinstance(item, Vertex):
            dialog = EditVertexDialog(item, parent=self.main_window)
            if dialog.exec() == QDialog.Accepted:
                updated_data = dialog.get_vertex_data()
                try:
                    self.diagram_model.update_vertex_properties(
                        item, 
                        x=updated_data['x'], y=updated_data['y'], 
                        label=updated_data['label'], 
                        vertex_type=updated_data['vertex_type']
                    )
                    self.status_message.emit(f"已更新顶点 {item.id} 的属性。")
                    self.update_all_views() # 更新后强制刷新视图
                except Exception as e:
                    self.status_message.emit(f"更新顶点属性失败: {e}")
                    QMessageBox.critical(self.main_window, "更新错误", f"更新顶点属性失败: {e}")
            else:
                self.status_message.emit(f"顶点 {item.id} 属性编辑已取消。")
        elif isinstance(item, Line):
            dialog = EditLineDialog(item, parent=self.main_window)
            if dialog.exec() == QDialog.Accepted:
                updated_data = dialog.get_line_data()
                try:
                    # 确保传递的是 Vertex 实例给 model
                    start_v = self.diagram_model.get_vertex_by_id(updated_data['v_start'].id)
                    end_v = self.diagram_model.get_vertex_by_id(updated_data['v_end'].id)
                    self.diagram_model.update_line_properties(
                        item, 
                        v_start=start_v, v_end=end_v, 
                        label=updated_data['label'], 
                        line_type=updated_data['line_type']
                    )
                    self.status_message.emit(f"已更新线条 {item.id} 的属性。")
                    self.update_all_views() # 更新后强制刷新视图
                except Exception as e:
                    self.status_message.emit(f"更新线条属性失败: {e}")
                    QMessageBox.critical(self.main_window, "更新错误", f"更新线条属性失败: {e}")
            else:
                self.status_message.emit(f"线条 {item.id} 属性编辑已取消。")


    def edit_selected_object_properties(self):
        """从导航栏菜单触发，编辑当前选中对象的属性。"""
        item = self.get_selected_item()
        self.edit_item_properties(item)

    # --- 文件操作 ---
    def save_diagram_to_file(self):
        """保存当前图到文件。"""
        file_path, _ = QFileDialog.getSaveFileName(self.main_window, "保存费曼图", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                self.diagram_model.save_to_json(file_path) # 假设 FeynmanDiagram 有 save_to_json 方法
                self.status_message.emit(f"图表已成功保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self.main_window, "保存失败", f"保存图表时发生错误：\n{str(e)}")
        else:
            self.status_message.emit("保存操作已取消。")

    def load_diagram_from_file(self):
        """从文件加载图。"""
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "加载费曼图", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                # FeynmanDiagram.load_from_json 应该返回一个新的 FeynmanDiagram 实例
                loaded_diagram = FeynmanDiagram.load_from_json(file_path)
                self.diagram_model = loaded_diagram # 替换当前模型
                self.update_all_views() # 加载后更新所有视图
                self.clear_selection() # 清除选中状态
                self.status_message.emit(f"图表已成功从 {file_path} 加载。")
            except Exception as e:
                QMessageBox.critical(self.main_window, "加载失败", f"加载图表时发生错误：\n{str(e)}")
        else:
            self.status_message.emit("加载操作已取消。")

    def clear_diagram(self):
        """
        清空图表，使用 PySide6 自带的 QMessageBox 进行二次确认。
        """
        reply = QMessageBox.question(
            self.main_window, # 父窗口
            "再次确认清空图表",       # 弹窗标题
            "再次确认：您确定要清空当前图表吗？此操作不可撤销。", # 弹窗消息
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
                QMessageBox.critical(self.main_window, "清空图表错误", f"清空图表失败: {e}")
        else:
            self.status_message.emit("清空图表操作已取消。")

    def undo(self):
        self.status_message.emit("执行撤销操作 (待实现)。")
        # self.diagram_model.undo() # 如果你的模型支持撤销
        # self.update_all_views()

    def redo(self):
        self.status_message.emit("执行重做操作 (待实现)。")
        # self.diagram_model.redo() # 如果你的模型支持重做
        # self.update_all_views()

    # --- 其他辅助方法 ---
    # 你可能还需要实现其他更复杂的交互，如多选，复制粘贴等。