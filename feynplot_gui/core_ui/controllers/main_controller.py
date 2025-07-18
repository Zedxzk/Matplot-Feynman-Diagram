# feynplot_GUI/feynplot_gui/controllers/main_controller.py
from typing import Optional, Tuple, Dict, Any, Union
from feynplot_gui.debug_utils import cout, cout3
from PySide6.QtCore import QObject, Signal, QPointF
from PySide6.QtWidgets import QMessageBox, QDialog, QFileDialog
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
from feynplot.core.line import Line, FermionLine, PhotonLine, GluonLine, LineStyle # 确保所有需要的线条类和样式被导入

# 导入主窗口 (方便类型提示和访问其子组件实例)
from feynplot_gui.core_ui.widgets.main_window import MainWindow
# 导入对话框，因为 MainController 现在负责它们的创建和数据显示
from feynplot_gui.core_ui.dialogs.add_vertex_dialog import AddVertexDialog
from feynplot_gui.core_ui.dialogs.edit_vertex_dialog import EditVertexDialog
from feynplot_gui.core_ui.dialogs.add_line_dialog import AddLineDialog
from feynplot_gui.core_ui.dialogs.edit_line_dialog import EditLineDialog
from feynplot_gui.core_ui.dialogs.delete_vertex_dialog import DeleteVertexDialog
from feynplot_gui.core_ui.dialogs.delete_line_dialog import DeleteLineDialog

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

        # 连接 MainController 自身的信号到主窗口的状态栏
        # self.status_message.connect(self.main_window.show_status_message)

        # 初始更新所有视图
        self.update_all_views()
        self.status_message.emit("应用程序已启动。")


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


        # --- LineListWidget 信号连接 ---
        # 用户的列表项点击事件 (现在只在 mousePressEvent 中发出)
        self.main_window.line_list_widget_instance.line_selected.connect(self.select_item)
        # 用户点击列表空白处事件 (现在只在 mousePressEvent 中发出)
        self.main_window.line_list_widget_instance.list_blank_clicked.connect(lambda: self.select_item(None))
        # 双击列表项事件
        self.main_window.line_list_widget_instance.line_double_clicked.connect(self._handle_list_line_double_clicked)


    # --- MainController 内部槽函数和公共方法 ---
    def set_diagram_model(self, loaded_diagram: FeynmanDiagram):
        """
        根据新加载的Diagram对象更新当前的diagram_model。
        方法：清空现有模型内容，然后将加载的元素逐一添加到现有模型中。
        """
        if not isinstance(loaded_diagram,FeynmanDiagram):
            raise TypeError("loaded_diagram 必须是 feynplot.core.diagram.Diagram 的实例。")

        # 1. 清空当前模型的所有内容
        # 重要：先移除线条，因为线条依赖顶点
        for line in list(self.diagram_model.lines): # 使用list()创建副本以安全迭代
            self.diagram_model.remove_line(line)
        for vertex in list(self.diagram_model.vertices): # 使用list()创建副本以安全迭代
            self.diagram_model.remove_vertex(vertex)

        # 2. 将加载的顶点和线条逐一添加到现有模型
        # 注意：这里需要确保添加线条时，其引用的顶点是当前模型中的顶点实例。
        # 最稳妥的方法是，先添加所有顶点，然后根据ID映射来连接线条。
        
        # 建立旧顶点ID到新顶点实例的映射（如果ID是唯一且稳定的）
        # 或者，如果loaded_diagram中的顶点是全新的实例，我们直接添加它们
        vertex_map = {} # 用于存储新旧顶点ID的映射，以便重新连接线条
        
        for vertex in loaded_diagram.vertices:
            # 假设 add_vertex 方法会处理将顶点添加到 self.diagram_model
            # 并且返回添加后的顶点实例（可能是同一个，也可能是拷贝后的新实例）
            # 我们需要保存这个新实例的引用，如果需要通过ID重新连接线条。
            self.diagram_model.add_vertex(vertex) # 直接添加新实例
            vertex_map[vertex.id] = vertex # 假设vertex.id是唯一的

        for line in loaded_diagram.lines:
            # 确保线条连接的是当前模型中的顶点实例
            start_v = vertex_map.get(line.start_vertex.id)
            end_v = vertex_map.get(line.end_vertex.id)
            line_type = vertex_map.get(line.line_type)

            if start_v and end_v:
                # 重新创建线条，确保它引用的是当前模型中的顶点对象
                new_line_instance = Line(start_vertex=start_v, end_vertex=end_v, **line.get_properties())
                print(new_line_instance)
                self.diagram_model.add_line(line=new_line_instance)
            else:
                print(f"警告: 无法为线条 {line.id} 找到对应的顶点，跳过此线条。")
                # 理论上，如果 import_diagram_from_json 逻辑正确，不应该出现这种情况。
                self.status_message.emit(f"警告: 无法加载线条 {line.id}，顶点缺失。")

        self.selected_item = None # 清除任何之前的选择

        # 3. 通知所有相关组件模型已更新并重新绘制
        # self.diagram_updated.emit()
        # self.selection_changed.emit(self.selected_item)
        self.update_all_views(canvas_options={'auto_scale': True})

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
                         line_options: Optional[Dict[str, Any]] = None
                        ):
        """
        强制所有视图重新绘制，并更新列表。
        当模型数据发生改变时，由 MainController 主动调用。
        """
        # 确保传入的字典不为 None，如果为 None 则使用空字典
        if picture_model:
            self.picture_model()
        canvas_opts = canvas_options if canvas_options is not None else {}
        vertex_opts = vertex_options if vertex_options is not None else {}
        line_opts = line_options if line_options is not None else {}
        
        # 将这些字典解包为关键字参数，传递给对应的控制器方法
        self.canvas_controller.update_canvas(**canvas_opts)
        self.vertex_controller.update_vertex_list(**vertex_opts)
        self.line_controller.update_line_list(**line_opts)
        
        # 更新其他可能需要刷新的 UI 元素，例如属性面板等
        self.status_message.emit("视图已更新。")


    def _handle_list_blank_clicked(self):
        """
        处理列表空白处被点击的信号，统一调用 select_item(None) 来清除所有选中。
        """
        print("列表空白处被点击，清除所有选中。")
        self.select_item(None) # 统一调用 select_item 方法，传入 None 表示取消所有选中


    def select_item(self, item: [Vertex, Line, None]):
        """
        统一管理应用程序中的选中状态。
        由各个子控制器（如 VertexController, CanvasController）直接调用。
        :param item: 要选中的 Vertex 或 Line 对象，或 None 表示清除选中。
        """
        print(f"\nMainController.select_item: 接收到项: {item}, 类型: {type(item)}") # 调试打印

        try:
            # 1. 首先清除之前选中项的 is_selected 状态
            if self._current_selected_item is not None:
                print(f"MainController: 清除旧选中项 {self._current_selected_item.id}.is_selected = False")
                self._current_selected_item.is_selected = False

            # 2. 更新 MainController 内部的当前选中项引用
            self._current_selected_item = item

            # 3. 如果有新选中项，设置其 is_selected 状态为 True
            if self._current_selected_item is not None:
                print(f"MainController: 设置新选中项 {self._current_selected_item.id}.is_selected = True")
                self._current_selected_item.is_selected = True

                item_type_str = ''
                if isinstance(self._current_selected_item, Vertex):
                    item_type_str = '顶点'
                elif isinstance(self._current_selected_item, Line):
                    item_type_str = '线条'

                self.status_message.emit(f"选中: {self._current_selected_item.id} ({item_type_str})")
                print(f"选中: {self._current_selected_item.id} ({item_type_str})")
                print(f"Current selected item (model ID): {self._current_selected_item.id}, is_selected: {self._current_selected_item.is_selected}")

            else:
                print("MainController: 取消选中所有项。")
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
            print(f"MainController: 选择项时发生错误: {e}")
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
                print(f"顶点: {v.id} is selected.")

        for l in self.diagram_model.lines:
            if l.is_selected:
                print(f"线条: {l.id} is selected.")

    def clear_selection(self):
        """清空当前选中状态。"""
        self.select_item(None) # 调用通用方法清空

    def get_selected_item(self) -> [Vertex, Line, None]:
        """获取当前选中项。"""
        return self._current_selected_item

        
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
        # parent_window = self.main_window if 
        # self.toolbox_controller.set_add_vertex_mode() # 切换工具箱模式
        # self.status_message.emit("请在画布上点击以添加顶点。")

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
                    self.update_all_views(canvas_options={'auto_scale': True}) # 添加后更新所有视图
                    self.select_item(new_vertex)  # 添加后选中新顶点
                    self.picture_model()
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

    def add_line_between_vertices(self, initial_start_vertex_id: str = None):
        """
        弹出对话框，允许用户选择两个顶点并添加一条线条。
        Args:
            initial_start_vertex_id (str, optional): 如果提供，将预设对话框中的起始顶点。
        """
        # Pass the initial_start_vertex_id to the dialog
        # The AddLineDialog constructor needs to be updated to accept this.
        dialog = AddLineDialog(
            vertices_data=self.diagram_model.vertices,
            parent=self.main_window,
            initial_start_vertex_id=initial_start_vertex_id # <--- Pass the new argument
        )

        if dialog.exec() == QDialog.Accepted:
            line_info = dialog.get_line_data()
            if line_info:
                final_v_start = line_info['v_start']
                final_v_end = line_info['v_end']

                if final_v_start == final_v_end:
                    QMessageBox.warning(self.main_window, "输入错误", "起始顶点和结束顶点不能相同！")
                    self.status_message.emit("线条添加失败: 起始顶点和结束顶点相同。")
                    return
                try:
                    new_line = self.diagram_model.add_line(
                        v_start=final_v_start,
                        v_end=final_v_end,
                        label=line_info.get('label', ''),
                        line_type=line_info['line_type']
                    )
                    self.status_message.emit(f"已添加线条: {new_line.id} 连接 {final_v_start.id} 和 {final_v_end.id}")
                    self.update_all_views()
                    self.select_item(new_line)
                    self.picture_model()
                except ValueError as e:
                    self.status_message.emit(f"添加线条失败: {e}")
                    QMessageBox.warning(self.main_window, "添加线条错误", f"添加线条失败: {e}")
                except Exception as e:
                    self.status_message.emit(f"添加线条时发生未知错误: {e}")
                    QMessageBox.critical(self.main_window, "添加线条错误", f"添加线条时发生未知错误: {e}")
            else:
                # self.status_message.emit("线条添加已取消。")
                print("线条添加已取消。")
        else:
            # self.status_message.emit("线条添加已取消。")
            print("线条添加已取消。")
            
        self.canvas_controller.reset_line_creation_state()


    def delete_selected_vertex(self, vertex_to_delete: Optional[Vertex] = None):
            """
            弹出对话框让用户选择或确认要删除的顶点，并执行删除操作。
            如果传入了 vertex_to_delete 参数，则直接预选并锁定该顶点。
            如果未传入，则尝试使用当前 UI 选中的顶点（如果存在），否则让用户选择。

            Args:
                vertex_to_delete (Optional[Vertex]): 可选参数，指定要删除的顶点实例。
                                                    如果提供，对话框将预选并锁定此顶点。
                                                    默认为 None。
            """
            # 1. 检查图中是否有顶点可供删除。如果没有，直接提示并返回。
            print(f"vertex_to_delete: {vertex_to_delete}") # 调试打印
            if not self.diagram_model.vertices:
                QMessageBox.information(self.main_window, "没有顶点", "图中目前没有可供删除的顶点。")
                self.status_message.emit("删除顶点失败：图中没有顶点。")
                return

            # 确定最终要传递给对话框的预选顶点
            final_pre_selected_vertex = vertex_to_delete
            if final_pre_selected_vertex is None:
                # 如果没有通过参数指定顶点，则尝试从 UI 获取当前选中的顶点
                # 假设 self.get_currently_selected_vertex() 返回一个 Vertex 实例或 None
                if hasattr(self, 'get_currently_selected_vertex') and callable(self.get_currently_selected_vertex):
                    final_pre_selected_vertex = self.get_currently_selected_vertex()
                elif hasattr(self, 'selected_vertex') and isinstance(self.selected_vertex, Vertex):
                    final_pre_selected_vertex = self.selected_vertex
                # 你需要根据你的实现调整这里获取选中顶点的方式，确保它返回一个 Vertex 对象或 None。

            # 2. 实例化删除顶点对话框，并传入当前图模型和最终确定的预选顶点
            dialog = DeleteVertexDialog(self.diagram_model, vertex_to_delete=final_pre_selected_vertex, parent=self.main_window)

            # 3. 显示对话框并等待用户交互
            if dialog.exec() == QDialog.Accepted:
                # 4. 如果用户点击了“确定”，获取用户选择的顶点ID
                selected_vertex_id = dialog.get_selected_vertex_id()
                print(f"Selected vertex ID: {selected_vertex_id}") # 调试打印
                
                if selected_vertex_id:
                    # 5. 再次获取选中顶点的对象，用于在消息中显示其标签
                    selected_vertex_obj = self.diagram_model.get_vertex_by_id(selected_vertex_id)
                    vertex_label = selected_vertex_obj.label if selected_vertex_obj else selected_vertex_id

                    # 6. 调用模型层的方法删除顶点
                    try:
                        if self.diagram_model.delete_vertex(selected_vertex_id):
                            # QMessageBox.information(self.main_window, "删除成功", 
                            #                         f"顶点 '{vertex_label}' (ID: {selected_vertex_id}) 及其关联线条已成功删除。")
                            self.status_message.emit(f"已删除顶点: {vertex_label} (ID: {selected_vertex_id})。")
                            self.picture_model()
                            self.update_all_views(canvas_options={'auto_scale': True}) # 删除后刷新视图
                            self.clear_selection() # 删除后清除当前选择（如果删除的是选中项）
                        else:
                            QMessageBox.warning(self.main_window, "删除失败", 
                                                f"无法删除顶点 '{vertex_label}' (ID: {selected_vertex_id})。")
                            self.status_message.emit(f"顶点 '{vertex_label}' (ID: {selected_vertex_id}) 删除失败。")
                    except Exception as e:
                        self.status_message.emit(f"删除顶点时发生未知错误: {e}")
                        QMessageBox.critical(self.main_window, "删除顶点错误", f"删除顶点时发生未知错误: {e}")
                else:
                    QMessageBox.warning(self.main_window, "删除失败", "未选择任何顶点。")
                    self.status_message.emit("删除顶点操作：未选择顶点。")
            else:
                # 7. 如果用户点击了“取消”
                self.status_message.emit("顶点删除操作已取消。")


    # --- 新增的 delete_selected_line 方法 ---
    def delete_selected_line(self, line_to_delete: Optional[Line] = None):
        """
        弹出对话框让用户选择或确认要删除的线条，并执行删除操作。
        如果传入了 line_to_delete 参数，则直接预选并锁定该线条。
        如果未传入，则尝试使用当前 UI 选中的线条（如果存在），否则让用户选择。

        Args:
            line_to_delete (Optional[Line]): 可选参数，指定要删除的线条实例。
                                              如果提供，对话框将预选并锁定此线条。
                                              默认为 None。
        """
        # 1. 检查图中是否有线条可供删除。如果没有，直接提示并返回。
        if not self.diagram_model.lines:
            QMessageBox.information(self.main_window, "没有线条", "图中目前没有可供删除的线条。")
            self.status_message.emit("删除线条失败：图中没有线条。")
            return

        # 确定最终要传递给对话框的预选线条
        final_pre_selected_line = line_to_delete
        if final_pre_selected_line is None:
            # 如果没有通过参数指定线条，则尝试从 UI 获取当前选中的线条
            # 假设 self.get_currently_selected_line() 返回一个 Line 实例或 None
            if hasattr(self, 'get_currently_selected_line') and callable(self.get_currently_selected_line):
                final_pre_selected_line = self.get_currently_selected_line()
            elif hasattr(self, 'selected_line') and isinstance(self.selected_line, Line):
                final_pre_selected_line = self.selected_line
            # 你需要根据你的具体 UI 实现来调整这里获取选中线条的方式。

        # 2. 实例化删除线条对话框，并传入当前图模型和最终确定的预选线条
        dialog = DeleteLineDialog(self.diagram_model, line_to_delete=final_pre_selected_line, parent=self.main_window)

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
        pass

    # --- 文件操作 ---
    def save_diagram_to_file(self):
        """保存当前图到文件。支持 .pdf, .png, .jpg 格式。"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.main_window, # Parent widget for the dialog
            "保存费曼图图像",  # Dialog title
            "",               # Default directory (empty means current)
            "PDF Files (*.pdf);;PNG Images (*.png);;JPEG Images (*.jpg);;All Files (*)" 
        )
        
        if not file_path:
            self.status_message.emit("保存操作已取消。")
            return
        # return
        try:
            print(f"文件路径: {file_path}")
            # 根据选择的过滤器确定扩展名
            extension_mapping = {
                "PDF Files (*.pdf)": ".pdf",
                "PNG Images (*.png)": ".png",
                "JPEG Images (*.jpg)": ".jpg"
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
            backend.savefig(file_path,
                             bbox_inches='tight', dpi=300
                             )
            print(f"图像已成功保存到: {file_path}")
            # self.status_message.emit(f"图像已成功保存到: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "保存失败",
                f"保存图像时发生错误：\n{str(e)}\n\n请检查文件路径和权限。"
            )
            self.status_message.emit(f"保存失败: {str(e)}")

    def clear_diagram(self):
        """
        清空图表，使用 PySide6 自带的 QMessageBox 进行二次确认。
        """
        reply = QMessageBox.question(
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
                QMessageBox.critical(self.main_window, "清空图表错误", f"清空图表失败: {e}")
        else:
            self.status_message.emit("清空图表操作已取消。")

    def save_diagram_from_toolbox(self):
        # QMessageBox.information(self.main_window, "提示", "save_diagram_from_toolbox")
        # exit()
        self.save_diagram_to_file()

    def save_diagram_from_navigation_bar(self):
        # QMessageBox().information(self.main_window, "提示", "save_diagram_from_navigation_bar")
        self.save_diagram_to_file()
    # --- 其他辅助方法 ---
    # 你可能还需要实现其他更复杂的交互，如多选，复制粘贴等。


    def edit_item_properties(self, item: Union[Vertex, Line]):
        """编辑顶点或线条的属性。"""
        if isinstance(item, Vertex):
            self.vertex_controller._on_edit_vertex_requested_from_list(item)
        elif isinstance(item, Line):
            self.line_controller._on_request_edit_line(item)    
    
    def picture_model(self):
        self.toolbox_controller._save_current_diagram_state()