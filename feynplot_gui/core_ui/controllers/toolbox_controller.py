# feynplot_gui/controllers/toolbox_controller.py

from PySide6.QtCore import QObject, Signal
import numpy as np  
# 导入 UI Widget
from feynplot_gui.core_ui.widgets.toolbox_widget import ToolboxWidget 
from collections import defaultdict 

class ToolboxController(QObject): # 继承自 QObject
    toggle_grid_visibility_requested = Signal() # <--- **新增信号**
    def __init__(self, toolbox_widget: ToolboxWidget, main_controller: 'MainController', parent=None): 
        super().__init__(parent) 

        self.toolbox_widget = toolbox_widget
        self.main_controller = main_controller 

        self.setup_buttons()

    def setup_buttons(self):
        """连接工具箱按钮的信号到 MainController 的相应方法，或本控制器内部的业务逻辑方法。"""
        
        # 删除操作
        self.toolbox_widget.delete_vertex_requested.connect(self.main_controller.delete_selected_object)
        self.toolbox_widget.delete_line_requested.connect(self.main_controller.delete_selected_object)
        
        # 清空图
        self.toolbox_widget.clear_diagram_requested.connect(self.main_controller.clear_diagram)
        self.toolbox_widget.request_auto_grid_adjustment.connect(self._auto_grid_adjustment_requested)
        # 顶点可见性信号
        self.toolbox_widget.show_all_vertices_requested.connect(self._handle_show_all_vertices)
        self.toolbox_widget.hide_all_vertices_requested.connect(self._handle_hide_all_vertices)

        # --- 顶点标签可见性信号连接 ---
        self.toolbox_widget.show_all_vertex_labels_requested.connect(self._handle_show_all_vertex_labels)
        self.toolbox_widget.hide_all_vertex_labels_requested.connect(self._handle_hide_all_vertex_labels)

        # --- 线标签可见性信号连接 ---
        self.toolbox_widget.show_all_line_labels_requested.connect(self._handle_show_all_line_labels)
        self.toolbox_widget.hide_all_line_labels_requested.connect(self._handle_hide_all_line_labels)

        # --- 【新增】自动调整画布信号连接 ---
        self.toolbox_widget.request_auto_scale.connect(self._on_request_auto_scale)
        self.toolbox_widget.request_auto_set_line_angles.connect(self._on_request_auto_set_line_angles)
        self.toolbox_widget.request_toggle_grid_visibility.connect(self._on_request_toggle_grid_visibility)
    def _handle_show_all_vertices(self):
        """
        处理“显示所有顶点”的请求。
        调用 MainController 的 diagram_model 的 show_all_vertices 方法，并更新视图。
        """
        self.main_controller.diagram_model.show_all_vertices()
        status_msg = "所有顶点已显示。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views() 

    def _handle_hide_all_vertices(self):
        """
        处理“隐藏所有顶点”的请求。
        调用 MainController 的 diagram_model 的 hide_all_vertices 方法，并更新视图。
        """
        self.main_controller.diagram_model.hide_all_vertices()
        status_msg = "所有顶点已隐藏。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views() 

    # --- 处理顶点标签可见性的方法 ---
    def _handle_show_all_vertex_labels(self):
        """
        处理“显示所有顶点标签”的请求。
        调用 MainController 的 diagram_model 的 show_all_vertice_labels 方法，并更新视图。
        """
        self.main_controller.diagram_model.show_all_vertice_labels()
        status_msg = "所有顶点标签已显示。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    def _handle_hide_all_vertex_labels(self):
        """
        处理“隐藏所有顶点标签”的请求。
        调用 MainController 的 diagram_model 的 hide_all_vertice_labels 方法，并更新视图。
        """
        self.main_controller.diagram_model.hide_all_vertice_labels()
        status_msg = "所有顶点标签已隐藏。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    # --- 处理线标签可见性的方法 ---
    def _handle_show_all_line_labels(self):
        """
        处理“显示所有线标签”的请求。
        调用 MainController 的 diagram_model 的 show_all_line_labels 方法，并更新视图。
        """
        # 假设你的 diagram_model 有一个 show_all_line_labels 方法
        self.main_controller.diagram_model.show_all_line_labels()
        status_msg = "所有线标签已显示。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    def _handle_hide_all_line_labels(self):
        """
        处理“隐藏所有线标签”的请求。
        调用 MainController 的 diagram_model 的 hide_all_line_labels 方法，并更新视图。
        """
        # 假设你的 diagram_model 有一个 hide_all_line_labels 方法
        self.main_controller.diagram_model.hide_all_line_labels()
        status_msg = "所有线标签已隐藏。"
        self.main_controller.status_message.emit(status_msg)
        self.main_controller.update_all_views()

    # --- 【新增】处理自动调整画布的槽函数 ---
    def _on_request_auto_scale(self):
        """
        处理“自动调整画布”按钮的请求。
        它会调用 MainController 的 update_all_views 方法，
        并传入 canvas_options={'auto_scale': True} 来强制画布进行一次自动缩放。
        """
        self.main_controller.status_message.emit("请求自动调整画布视图。")
        self.main_controller.update_all_views(canvas_options={'auto_scale': True})


    def update_tool_mode(self, mode: str):
        """
        根据 MainController 传递的当前工具模式更新工具箱按钮的选中状态。
        """
        # Note: Your ToolboxWidget now primarily uses push buttons for actions,
        # not necessarily radio buttons for "modes" like select/add.
        # This part might need re-evaluation or removal based on your interaction design.
        if hasattr(self.toolbox_widget, 'add_vertex_button') and mode == 'add_vertex':
            self.toolbox_widget.add_vertex_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'add_line_button') and mode == 'add_line':
            self.toolbox_widget.add_line_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'selection_button') and mode == 'select':
            self.toolbox_widget.selection_button.setChecked(True)
        else:
            if hasattr(self.toolbox_widget, 'add_vertex_button'): self.toolbox_widget.add_vertex_button.setChecked(False)
            if hasattr(self.toolbox_widget, 'add_line_button'): self.toolbox_widget.add_line_button.setChecked(False)
            if hasattr(self.toolbox_widget, 'selection_button'): self.toolbox_widget.selection_button.setChecked(False)
            
        self.main_controller.status_message.emit(f"工具箱工具模式已更新为：{mode}")

    def update(self):
        """通用的更新方法，目前不需要额外逻辑。"""
        pass

    def _on_request_auto_set_line_angles(self):
        """
        处理“自动设置线角度”按钮的请求。
        它会遍历所有边，根据是否存在连接相同两个顶点的多重边（平行边）来设置 angle_bias。
        自循环边（v_start == v_end）将有单独的默认处理。
        所有角度值都以**度**为单位。
        """
        diagram_model = self.main_controller.diagram_model
        lines = diagram_model.lines

        # 步骤 1: 根据它们连接的唯一顶点对对线进行分组
        # 使用 frozenset 作为可哈希的、不依赖顺序的键
        # 我们会先分离出自循环边
        vertex_pair_to_lines = defaultdict(list)
        self_loops = []

        for line in lines:
            if line.v_start == line.v_end:
                self_loops.append(line)
            else:
                # 为顶点对创建不依赖顺序的键
                vertex_key = frozenset({line.v_start.id, line.v_end.id})
                vertex_pair_to_lines[vertex_key].append(line)

        lines_processed = set() # 跟踪已调整的线

        # ---
        ## 步骤 2: 处理多重边（平行边）

        for vertex_key, connected_lines_group in vertex_pair_to_lines.items():
            num_parallel_lines = len(connected_lines_group)

            if num_parallel_lines < 2:
                # 这组只有一条线，不需要为平行边设置特殊偏差
                # 如果没有被处理过，它将在后面作为“默认”线处理
                continue

            # 将这些线添加到已处理集合中
            for line in connected_lines_group:
                lines_processed.add(line)

            if num_parallel_lines == 2:
                # 两条边共顶点 (连接相同两个顶点)
                line1, line2 = connected_lines_group
                line1.reset_angles(90)  # 直接使用度数 45
                line2.reset_angles(-90) # 直接使用度数 -45

            elif num_parallel_lines == 3:
                # 三条边共顶点 (连接相同两个顶点)
                # 按其特定类型（例如 FermionLine, PhotonLine）对线进行分组
                line_types_grouped = defaultdict(list)
                for line in connected_lines_group:
                    # 使用 type(line) 作为标识符。确保您的 Line 类是不同的。
                    line_types_grouped[type(line)].append(line) 
                
                # 检查三条线是否都是相同类型
                if len(line_types_grouped) == 1:
                    # 所有三条线都是相同类型
                    # 按照检索顺序应用偏差（不随机洗牌）
                    ordered_lines = list(connected_lines_group) 
                    
                    ordered_lines[0].reset_angles(60)  # 直接使用度数 60
                    ordered_lines[1].reset_angles(-60) # 直接使用度数 -60
                    ordered_lines[2].reset_angles(0)   # 直接使用度数 0
                    
                elif len(line_types_grouped) == 2:
                    # 两种类型: 两条线一种类型，一条线另一种类型
                    odd_one_out_line = None
                    matching_lines = []

                    for line_type, lines_of_type in line_types_grouped.items():
                        if len(lines_of_type) == 1:
                            odd_one_out_line = lines_of_type[0]
                        else:
                            matching_lines.extend(lines_of_type)
                    
                    if odd_one_out_line:
                        odd_one_out_line.reset_angles(0) # 不同类型得到 0 偏差
                    
                    # 剩下的两条（匹配的）线得到 +/- 60
                    if len(matching_lines) == 2:
                        matching_lines[0].reset_angles(60)  # 直接使用度数 60
                        matching_lines[1].reset_angles(-60) # 直接使用度数 -60
                else:
                    # 针对 3 条线出现意外类型数量的备用方案（不应该发生）
                    # 或者如果存在超过 3 条平行线（逻辑未指定）
                    for line in connected_lines_group:
                        line.reset_angles(0) # 未处理情况的默认无偏差
            
            # 对于 num_parallel_lines > 3 的情况，您需要在此处定义具体的逻辑。
            # 目前，它们将直接进入下一步并获得默认的 0 偏差。

        # ---
        ## 步骤 3: 处理自循环边和其它非平行线（angle_bias = 0）

        for line in lines:
            if line in lines_processed:
                continue # 已作为平行边组的一部分进行处理

            if line in self_loops:
                # 为自循环边应用默认偏差，使其呈现为弧形
                # 这将使它们与直线区分开来。根据需要调整。
                line.reset_angles(90) # 直接使用度数 90
            else:
                # 不属于平行边组且不是自循环的线
                # 获得 0 的偏差（即它们在端点之间的自然角度）
                line.reset_angles(0)


        # 更新角度后，通知 MainController 刷新视图
        self.main_controller.status_message.emit("已自动设置所有线角度。")
        self.main_controller.update_all_views()


    def _auto_grid_adjustment_requested(self):
        """
        处理“自动调整网格”按钮的请求。
        遍历模型中的所有顶点，将其坐标调整到最近的整数格点。
        """
        print("执行自动调整格点操作...")

        if not self.main_controller.diagram_model:
            print("错误：diagram_model 未初始化。")
            return

        # 获取所有顶点
        vertices_to_update = self.main_controller.diagram_model.vertices

        if not vertices_to_update:
            print("图中没有顶点可供调整。")
            return

        # 记录是否发生了实际的调整，用于决定是否需要更新视图
        changes_made = False

        for vertex in vertices_to_update:
            original_x = vertex.x
            original_y = vertex.y

            # 将坐标四舍五入到最近的整数
            new_x = int(np.round(original_x))
            new_y = int(np.round(original_y))

            # 检查坐标是否发生变化
            if new_x != original_x or new_y != original_y:
                vertex.x = new_x
                vertex.y = new_y
                changes_made = True
                print(f"顶点 {vertex.id} 从 ({original_x:.2f}, {original_y:.2f}) 调整到 ({new_x}, {new_y})")

        if changes_made:
            self.main_controller.update_all_views(canvas_options={'auto_scale': True}) # 更新所有相关的视图，包括画布
            print("自动调整格点完成，视图已更新。")
        else:
            print("所有顶点已在格点上，无需调整。")
            print("没有顶点需要调整。")

    def _on_request_toggle_grid_visibility(self):
        """
        处理“切换网格可见性”按钮的请求。
        它会调用 MainController 的 diagram_model 的 toggle_grid_visibility 方法，
        并更新视图。
        """
        self.toggle_grid_visibility_requested.emit() # <--- **发出信号**
        print(f"Grid visibility toggled. Current state: {self.main_controller.canvas_controller._canvas_instance.grid_on}")

        self.main_controller.update_all_views()