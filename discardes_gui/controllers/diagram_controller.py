# gui/controllers/diagram_controller.py
import numpy as np
from typing import Dict, Any, List, Optional

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem # <--- ADD QGraphicsItem HERE
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QDialog
from gui.widgets.add_line_dialog import AddLineDialog

# 导入核心 feynplot 模块
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    GluonLine, PhotonLine, WPlusLine, WMinusLine, ZBosonLine,
    FermionLine, AntiFermionLine, Line
)

# 导入自定义图形项 (注意相对路径导入)
from ..widgets.custom_graphics_items import GraphicsVertex, GraphicsLine
# diagram_controller.py（添加 import）
from gui.widgets.add_vertex_dialog import AddVertexDialog


class DiagramController:
    """
    负责费曼图数据模型 (FeynmanDiagram) 和图形视图 (QGraphicsScene/View) 之间的交互逻辑。
    它处理用户输入，更新数据模型，并确保图形视图的显示与数据模型同步。
    """
    def __init__(self, diagram_model: FeynmanDiagram, scene: QGraphicsScene, view: QGraphicsView):
        self.diagram_model = diagram_model # 费曼图数据模型
        self.scene = scene # QGraphicsScene 实例
        self.view = view # QGraphicsView 实例
        
        # 建立数据模型对象到 QGraphicsItem 的映射，方便快速查找
        self.vertex_item_map: Dict[Vertex, GraphicsVertex] = {}
        self.line_item_map: Dict[Line, GraphicsLine] = {} 

    # --- 视图交互逻辑 ---
    def zoom_event(self, event):
        """
        处理 QGraphicsView 的鼠标滚轮事件，实现视图的缩放功能。
        同时确保 QGraphicsScene 的区域足够大以避免图形被裁切。
        """
        zoom_in_factor = 1.25  # 放大因子
        zoom_out_factor = 1 / zoom_in_factor  # 缩小因子

        # 根据滚轮方向确定缩放因子
        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
        else:
            factor = zoom_out_factor

        # 设置变换锚点为鼠标位置，实现以鼠标为中心的缩放
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.scale(factor, factor)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        # 关键：更新场景区域为所有图形项的边界矩形，避免放大后被裁切
        bounding_rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(bounding_rect)


    # --- 数据初始化和绘制逻辑 ---
    def initialize_diagram_data(self):
        """
        初始化一些用于演示的费曼图顶点和线条数据。
        """
        # 添加普通顶点
        v1 = self.diagram_model.add_vertex(0, 0, label='A')
        v2 = self.diagram_model.add_vertex(50, 50, label='B')
        # 添加结构化顶点（具有自定义外观）
        v_struct1 = self.diagram_model.add_vertex(
            -20, 20, label=r'Struct$_1$', is_structured=True,
            structured_radius=0.8, structured_facecolor='lightblue', label_offset=(0, 0.9),
            use_custom_hatch=True, custom_hatch_line_color='darkred', custom_hatch_line_width=1.0,
            custom_hatch_line_angle_deg=60, custom_hatch_spacing_ratio=0.08
        )
        
        # 添加线条，连接顶点并指定线条类型和绘图配置
        self.diagram_model.add_line(v1, v2, GluonLine(label='g', line_plot_config={'color': 'purple', 'linewidth': 2.0}))
        self.diagram_model.add_line(v1, v_struct1, PhotonLine(label=r'$\gamma$', line_plot_config={'color': 'orange'}))

    def add_test_vertex(self):
        """
        弹出输入对话框添加一个顶点，如果确认则加入模型并绘制。
        """
        dialog = AddVertexDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            coords = dialog.get_coordinates()
            if coords is not None:
                x, y = coords
                vertex = self.diagram_model.add_vertex(
                    x, y, label=f"v{len(self.diagram_model.vertices)}"
                )
                self.add_graphics_vertex(vertex)
                self.scene.update()

    def add_graphics_line(self, line_data: Line):
        """
        为给定的 Line 数据对象创建 GraphicsLine 并添加到 QGraphicsScene。
        同时维护数据模型对象与图形项之间的映射。
        """
        # 获取线条连接的起始和结束顶点的 GraphicsItem 实例
        start_item = self.vertex_item_map.get(line_data.v_start)
        end_item = self.vertex_item_map.get(line_data.v_end)

        if start_item and end_item:
            # 创建 GraphicsLine 实例，并传入其连接的图形顶点
            graphics_line = GraphicsLine(line_data, start_item, end_item)
            self.scene.addItem(graphics_line) # 将图形项添加到场景
            self.line_item_map[line_data] = graphics_line # 存储映射
        else:
            print(f"警告: 无法为线条 {line_data.label} 找到起始或结束图形顶点。")

    def add_graphics_vertex(self, vertex_data: Vertex):
        """
        为给定的 Vertex 数据对象创建 GraphicsVertex 并添加到 QGraphicsScene。
        同时维护数据模型对象与图形项之间的映射。
        """
        graphics_vertex = GraphicsVertex(vertex_data)
        self.scene.addItem(graphics_vertex)  # 添加到 QGraphicsScene
        self.vertex_item_map[vertex_data] = graphics_vertex  # 添加到映射表

    def draw_diagram_in_scene(self):
        """
        清空 QGraphicsScene 并根据当前的费曼图数据模型重新绘制所有顶点和线条。
        """
        self.scene.clear() # 清空场景中的所有图形项
        self.vertex_item_map.clear() # 清空所有映射
        self.line_item_map.clear()

        # 先遍历并绘制所有顶点
        for vertex_data in self.diagram_model.vertices:
            self.add_graphics_vertex(vertex_data)

        # 再遍历并绘制所有线条
        for line_data in self.diagram_model.lines:
            self.add_graphics_line(line_data)

        self.scene.update() # 请求场景更新显示

    def add_test_line(self):
        if len(self.diagram_model.vertices) < 2:
            print("需要至少两个顶点才能添加线条。")
            return

        dialog = AddLineDialog(self.diagram_model.vertices)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            v_start, v_end, particle_type = dialog.get_selected_data()
            if v_start == v_end:
                print("起点和终点不能相同！")
                return

            # 根据粒子类型选择对应线条类
            line_cls_map = {
                "费米子": FermionLine,
                "反费米子": AntiFermionLine,
                "光子": PhotonLine,
                "胶子": GluonLine,
                "W+": WPlusLine,
                "W-": WMinusLine,
                "Z玻色子": ZBosonLine,
            }

            print("已有顶点列表:")
            for v in self.diagram_model.vertices:
                print(f"顶点: {v}, id: {id(v)}")

            print("选中起点和终点:")
            print(v_start, id(v_start))
            print(v_end, id(v_end))
            
            # --- 关键修改在这里：为 Line 实例提供默认的 line_plot_config ---
            # 这里的默认颜色是灰色，你可以根据需要修改
            default_line_config = {'color': 'gray', 'linewidth': 1.0}
            
            line_type_instance = line_cls_map.get(particle_type, FermionLine)(
                v_start=v_start, 
                v_end=v_end, 
                line_plot_config=default_line_config # <--- 添加此参数
            ) 
            print("添加的线条类型: " + particle_type)
            
            new_line = self.diagram_model.add_line(
                v_start=v_start,
                v_end=v_end,
                line=line_type_instance # <--- 这里传递的是实例
            )
            if new_line is None:
                print("添加线条失败，可能已存在相同线条。")
            else:
                self.add_graphics_line(new_line) # 添加到 QGraphicsScene
                self.scene.update() # 请求场景更新显示

    def get_selected_item_data(self, graphics_item: QGraphicsItem) -> Optional[Any]:
        """
        从一个 QGraphicsItem 中获取其关联的底层数据模型对象 (Vertex 或 Line)。
        """
        if hasattr(graphics_item, 'vertex_data'):
            return graphics_item.vertex_data
        elif hasattr(graphics_item, 'line_data'):
            return graphics_item.line_data
        return None

    # --- 数据同步和更新逻辑 ---
    def update_item_label(self, item_data: Any, new_label: str):
        """
        更新数据模型对象的标签，并同步更新其对应的图形项的标签显示。
        """
        if hasattr(item_data, 'label'):
            item_data.label = new_label # 更新数据模型
            # 根据数据模型的类型，找到对应的图形项并更新其标签
            if isinstance(item_data, Vertex) and item_data in self.vertex_item_map:
                graphics_item = self.vertex_item_map[item_data]
                graphics_item.label_item.setPlainText(new_label) # 直接更新 GraphicsVertex 的标签文本
            elif isinstance(item_data, Line) and item_data in self.line_item_map:
                graphics_item = self.line_item_map[item_data]
                graphics_item.update_path() # 调用 GraphicsLine 的 update_path 方法来重绘和更新标签
            self.scene.update() # 请求场景刷新以显示更新

    def update_item_position(self, vertex_data: Vertex, new_x: float, new_y: float):
        """
        更新顶点数据模型在费曼图中的位置。
        注意：GraphicsVertex 自身在 ItemPositionHasChanged 信号中会更新其自身的位置，
        这里主要是同步数据模型。
        """
        vertex_data.x = new_x
        vertex_data.y = new_y
        # 这里不需要手动调用 GraphicsVertex.setPos，因为它已经被 GraphicsVertex 的 itemChange 处理器更新了
        # 重要的是要确保所有连接到此顶点的线条也能更新其图形路径。

    def update_lines_connected_to_vertex(self, vertex_data: Vertex):
        """
        遍历所有线条，如果线条的起始或结束顶点是给定的 `vertex_data`，
        则更新对应 GraphicsLine 的路径，以反映顶点位置的变化。
        """
        for line_data in self.diagram_model.lines:
            if line_data.v_start == vertex_data or line_data.v_end == vertex_data:
                if line_data in self.line_item_map:
                    self.line_item_map[line_data].update_path() # 请求 GraphicsLine 重新绘制路径
        self.scene.update() # 请求场景刷新