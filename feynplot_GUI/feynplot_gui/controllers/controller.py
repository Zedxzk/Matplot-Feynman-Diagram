# feynplot_GUI/feynplot_gui/controller.py

from PySide6.QtCore import QObject, Signal
from feynplot.core.diagram import FeynmanDiagram
# 导入所有可能用到的核心模型类
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line, FermionLine, PhotonLine
from ..mouse_event_handler import MouseEventHandler
from ..item_manager import ItemManager # 假设 ItemManager 存在且管理添加/删除/编辑逻辑
from PySide6.QtWidgets import QListWidget # 导入 QListWidget

class Controller(QObject):
    # 定义信号，当图数据发生变化时发出，通知视图更新
    diagram_updated = Signal()
    selection_changed = Signal(object) # 当选中项改变时发出
    item_properties_edited = Signal(object) # 当项的属性被编辑时发出
    status_message = Signal(str) # 用于显示状态信息

    # 改变 __init__ 方法的签名，使其接收所需的 UI 组件
    def __init__(self, canvas_widget, vertex_list_widget, line_list_widget):
        super().__init__()
        # self.main_window = main_window # 这个可以在后面通过 self.ctrl.main_window = self 赋值
        
        # 存储传入的 UI 组件引用
        self.canvas = canvas_widget
        self.vertex_list_widget = vertex_list_widget
        self.line_list_widget = line_list_widget

        self.diagram_model = FeynmanDiagram() # 初始化数据模型

        self.mouse_event_handler = MouseEventHandler(self)
        self.mouse_event_handler.connect_events() # 连接鼠标事件

        self.item_manager = ItemManager(self) # 初始化 ItemManager

        self.highlighter = Highlighter(self) # 初始化 Highlighter

        self.canvas.set_diagram_data(self.diagram_model) # 将数据模型传递给画布

        self.initialize_diagram_data() # 初始化一些示例数据


        # 3. 数据已经填充完毕，现在触发第一次视图更新
        # 移除或注释掉 main_window.py 中的 self.ctrl.item_manager.update_list_widgets()
        # 这里也不再需要 item_manager.update_list_widgets()，因为它应该由 diagram_updated 信号处理
        # 而是直接调用 update_view，它会发出 diagram_updated 信号

        # 连接信号到列表视图的更新方法
        self.diagram_updated.connect(self._update_list_views)
        self.selection_changed.connect(self._update_list_selection)
        self.update_view() # <--- 关键：在数据初始化后立即触发完整视图更新
        
        print("Controller initialized and initial view update triggered.")


    def initialize_diagram_data(self):
        """
        初始化费曼图的示例数据。
        """
        print("\nDEBUG: Initializing diagram data and checking line vertices...") 

        # # 使用 add_vertex 直接传入坐标和属性来创建顶点
        # v_e_in = self.diagram_model.add_vertex(x=-5, y=0, label="e- (Electron In)", color='blue')
        # v_e_out = self.diagram_model.add_vertex(x=5, y=0, label="e- (Electron Out)", color='blue')
        # v_photon = self.diagram_model.add_vertex(x=0, y=0, label="γ (Photon Emission)", color='green', size=15)
        # v_mu_in = self.diagram_model.add_vertex(x=0, y=-5, label="μ- (Muon In)", color='red')
        # v_mu_out = self.diagram_model.add_vertex(x=0, y=-10, label="μ- (Muon Out)", color='red') 

        # # print("\n--- Vertices Created ---")
        # # print(f"v_e_in: ({v_e_in.x}, {v_e_in.y})")
        # # print(f"v_e_out: ({v_e_out.x}, {v_e_out.y})")
        # # print(f"v_photon: ({v_photon.x}, {v_photon.y})")
        # # print(f"v_mu_in: ({v_mu_in.x}, {v_mu_in.y})")
        # # print(f"v_mu_out: ({v_mu_out.x}, {v_mu_out.y})")
        # # print("------------------------")

        # # # 直接通过传入顶点和线条类型构造线条，并指定其他属性
        # # print("\n--- Adding Lines and Checking Vertices ---")

        # # Line 1: Electron In -> Photon Emission
        # line1 = self.diagram_model.add_line(
        #     v_start=v_e_in, v_end=v_photon, 
        #     line_type=FermionLine, 
        #     label="e- (Electron In -> Photon Emission)", 
        #     arrow=True, 
        #     color='green'
        # ) 
        # # # 检查 Line 1
        # # print(f"Line '{line1.label}' (ID: {line1.id}):")
        # # print(f"  Start: ({line1.v_start.x}, {line1.v_start.y}) -> End: ({line1.v_end.x}, {line1.v_end.y})")
        # # print(f"   Arrow: {line1.linePlotConfig.get('arrow', False)}, Color: {line1.linePlotConfig.get('color', 'N/A')}")

        # # Line 2: Photon Emission -> Electron Out
        # line2 = self.diagram_model.add_line(
        #     v_start=v_photon, v_end=v_e_out, 
        #     line_type=FermionLine, 
        #     label="e- (Photon Emission -> Electron Out)", 
        #     arrow=True
        # )
        # # 检查 Line 2
        # # print(f"Line '{line2.label}' (ID: {line2.id}):")
        # # print(f"  Start: ({line2.v_start.x}, {line2.v_start.y}) -> End: ({line2.v_end.x}, {line2.v_end.y})")
        # # print(f"   Arrow: {line2.linePlotConfig.get('arrow', False)}, Color: {line2.linePlotConfig.get('color', 'N/A')}")


        # # Line 3: Electron Out -> Muon In
        # line3 = self.diagram_model.add_line(
        #     v_start=v_e_out, v_end=v_mu_in, 
        #     line_type=PhotonLine, 
        #     label="γ (Electron Out -> Muon In)", 
        #     # linestyle='--'
        # ) 
        # # 检查 Line 3
        # # print(f"Line '{line3.label}' (ID: {line3.id}):")
        # # print(f"  Start: ({line3.v_start.x}, {line3.v_start.y}) -> End: ({line3.v_end.x}, {line3.v_end.y})")
        # # print(f"  LineStyle (Plot): {line3.linePlotConfig.get('linestyle', 'N/A')}")


        # # Line 4: Muon In -> Muon Out
        # line4 = self.diagram_model.add_line(
        #     v_start=v_mu_in, v_end=v_mu_out, 
        #     line_type=FermionLine, 
        #     label="μ- (Muon In -> Muon Out)", 
        #     arrow=True
        # )
        # # 检查 Line 4
        # print(f"Line '{line4.label}' (ID: {line4.id}):")
        # print(f"  Start: ({line4.v_start.x}, {line4.v_start.y}) -> End: ({line4.v_end.x}, {line4.v_end.y})")
        # print(f"  Arrow: {line4.linePlotConfig.get('arrow', False)}")
        # print("------------------------------------------")
        
        # self.update_view() # 确保视图在初始化后更新
        # print("DEBUG: Diagram data initialized and view updated.")

    def update_view(self):
        """通知画布更新其显示。"""
        self.canvas.update_canvas()
        self.diagram_updated.emit() # 发送信号，通知其他UI部分（如列表）更新

    def select_item_at_coords(self, x_data, y_data):
        """在给定坐标处选择一个图元素。"""
        selected_item = self.mouse_event_handler._get_item_at_coords(x_data, y_data)
        self.highlighter.select_item(selected_item) # 调用 highlighter 的选择方法

    def get_selected_item(self):
        """获取当前选中的元素。"""
        return self.highlighter.get_selected_item()

    def _update_list_views(self):
        """更新顶点和线条列表视图的内容。"""
        self.vertex_list_widget.clear()
        for vertex in self.diagram_model.vertices:
            self.vertex_list_widget.addItem(f"{vertex.label} (ID: {vertex.id}) @ ({vertex.x:.1f}, {vertex.y:.1f})")
        
        self.line_list_widget.clear()
        for line in self.diagram_model.lines:
            start_id = line.v_start.id if line.v_start else "N/A"
            end_id = line.v_end.id if line.v_end else "N/A"
            self.line_list_widget.addItem(f"{line.label} (ID: {line.id}) from {start_id} to {end_id}")

    def _update_list_selection(self, selected_item):
        """根据当前选中的图元素更新列表视图的选中状态。"""
        self.vertex_list_widget.clearSelection()
        self.line_list_widget.clearSelection()

        if selected_item:
            if isinstance(selected_item, Vertex):
                for i in range(self.vertex_list_widget.count()):
                    item_text = self.vertex_list_widget.item(i).text()
                    if f"(ID: {selected_item.id})" in item_text:
                        self.vertex_list_widget.item(i).setSelected(True)
                        break
            elif isinstance(selected_item, Line):
                for i in range(self.line_list_widget.count()):
                    item_text = self.line_list_widget.item(i).text()
                    if f"(ID: {selected_item.id})" in item_text:
                        self.line_list_widget.item(i).setSelected(True)
                        break

# 假设 Highlighter 类如下，你需要根据实际路径导入或定义它
class Highlighter:
    def __init__(self, controller):
        self.ctrl = controller
        self._selected_item = None

    def select_item(self, item):
        """选择一个元素并更新高亮。"""
        if self._selected_item != item:
            self._selected_item = item
            self.ctrl.canvas.set_highlighted_artist(item) # 让画布知道哪个元素应该被高亮
            self.ctrl.selection_changed.emit(item) # 发出选择改变信号

    def clear_selection(self):
        """清除所有选择。"""
        if self._selected_item is not None:
            self._selected_item = None
            self.ctrl.canvas.clear_highlight() # 让画布清除高亮
            self.ctrl.selection_changed.emit(None) # 发出选择改变信号，表示没有选中项

    def get_selected_item(self):
        return self._selected_item