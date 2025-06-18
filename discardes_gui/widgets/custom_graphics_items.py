# gui/widgets/custom_graphics_items.py
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui import QPainterPath, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QPointF

# 导入核心 feynplot 模块的数据结构
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line

# diagram_controller.py（添加 import）
# from gui.widgets.add_vertex_dialog import AddVertexDialog
# from feynplot.core.vertex import Vertex


class GraphicsVertex(QGraphicsEllipseItem):
    """
    表示费曼图顶点的 QGraphicsItem。
    它封装了 Vertex 数据模型对象，并处理其图形表示和基本交互。
    """
    def __init__(self, vertex_data: Vertex, radius: float = 0.5):
        # 初始化 QGraphicsEllipseItem，设置其为圆形
        super().__init__(-radius, -radius, 2 * radius, 2 * radius) 
        self.vertex_data = vertex_data # 存储关联的 Vertex 数据对象
        self.setPos(vertex_data.x, vertex_data.y) # 设置图形项在场景中的位置

        # 设置顶点的颜色和边框样式
        self.setBrush(QBrush(QColor(vertex_data.structured_facecolor if vertex_data.is_structured else "blue")))
        self.setPen(QPen(QColor(vertex_data.structured_edgecolor if vertex_data.is_structured else "darkblue"), 
                         vertex_data.structured_linewidth if vertex_data.is_structured else 1.0))

        # 启用图形项的交互功能
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable) # 可移动
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable) # 可选中
        # 当图形项的位置或几何形状改变时，发送通知
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges) 

        # 为顶点添加标签
        self.label_item = QGraphicsTextItem(vertex_data.label, parent=self)
        self.label_item.setFont(QFont("Times New Roman", 12))
        self.label_item.setDefaultTextColor(QColor("black")) 
        
        # 调整标签位置，使其相对于顶点居中或按偏移量显示
        text_rect = self.label_item.boundingRect()
        label_x_offset = -text_rect.width() / 2 + vertex_data.label_offset[0]
        label_y_offset = -radius - text_rect.height() + vertex_data.label_offset[1]
        self.label_item.setPos(label_x_offset, label_y_offset)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """
        处理图形项状态变化的事件。
        当顶点位置或选中状态改变时，通知控制器。
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # 当顶点位置改变时，通知 DiagramController 更新数据模型和相关线条
            if self.scene() and hasattr(self.scene(), '_diagram_controller'):
                # 获取顶点在场景中的新位置
                new_scene_pos = self.scenePos()
                self.scene()._diagram_controller.update_item_position(
                    self.vertex_data, new_scene_pos.x(), new_scene_pos.y()
                )
                # 触发连接到此顶点的线条的更新
                self.scene()._diagram_controller.update_lines_connected_to_vertex(self.vertex_data)

        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            # 当选中状态改变时，QGraphicsScene 会发出 selectionChanged 信号，
            # mainwindow 会监听并处理属性面板的更新，所以这里无需直接操作 property_panel
            if self.scene() and hasattr(self.scene(), '_main_window'):
                if value: # 被选中
                    pass # 逻辑已在 mainwindow._on_selection_changed 处理
                else: # 取消选中
                    pass # 逻辑已在 mainwindow._on_selection_changed 处理
        return super().itemChange(change, value)


class GraphicsLine(QGraphicsPathItem):
    """
    表示费曼图线条的 QGraphicsItem。
    它封装了 Line 数据模型对象，并根据连接的 GraphicsVertex 绘制路径。
    """
    def __init__(self, line_data: Line, start_vertex_item: GraphicsVertex, end_vertex_item: GraphicsVertex):
        super().__init__()
        self.line_data = line_data # 存储关联的 Line 数据对象
        self.start_vertex_item = start_vertex_item # 关联的起始 GraphicsVertex
        self.end_vertex_item = end_vertex_item # 关联的结束 GraphicsVertex

        # 根据 line_data 的 plot_config 设置线条样式
        plot_properties = self.line_data.get_plot_properties() 
        pen_color = QColor(plot_properties.get('color', 'black'))
        pen_width = plot_properties.get('linewidth', 1.0)
        
        linestyle_str = plot_properties.get('linestyle', '-')
        pen_style = Qt.PenStyle.SolidLine # 默认实线
        if linestyle_str == '--':
            pen_style = Qt.PenStyle.DashLine
        elif linestyle_str == '-.':
            pen_style = Qt.PenStyle.DashDotLine
        elif linestyle_str == ':':
            pen_style = Qt.PenStyle.DotLine

        self.setPen(QPen(pen_color, pen_width, pen_style))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable) # 可选中

        self.label_item = None # 用于存储线条标签的 QGraphicsTextItem
        self.update_path() # 初始化绘制线条路径和标签

    def update_path(self):
        """
        更新线条的路径和标签位置。
        当连接的顶点移动时，此方法会被调用以重绘线条。
        """
        path = QPainterPath()
        # 获取起始和结束 GraphicsVertex 在场景中的位置
        start_point = self.start_vertex_item.scenePos()
        end_point = self.end_vertex_item.scenePos()

        path.moveTo(start_point)
        path.lineTo(end_point) # 简单的直线，未来可扩展为贝塞尔曲线等
        self.setPath(path)

        # 更新线条标签
        if self.line_data.label:
            # 移除旧的标签（如果有的话）
            if self.label_item and self.label_item in self.childItems():
                self.scene().removeItem(self.label_item)
            
            mid_point = (start_point + end_point) / 2 # 计算线条中点
            self.label_item = QGraphicsTextItem(self.line_data.label, parent=self)
            
            label_properties = self.line_data.get_label_properties()
            self.label_item.setFont(QFont("Times New Roman", label_properties.get('fontsize', 10)))
            self.label_item.setDefaultTextColor(QColor(label_properties.get('color', "darkgray")))
            
            # 设置标签位置，考虑偏移量
            self.label_item.setPos(mid_point.x() + self.line_data.label_offset[0],
                                  mid_point.y() + self.line_data.label_offset[1])
        elif self.label_item: # 如果数据模型没有标签了，但图形项还有，则移除
            self.scene().removeItem(self.label_item)
            self.label_item = None