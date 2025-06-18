import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QWidget, QPushButton, QDockWidget, QLabel, QLineEdit, QFormLayout,
    QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsItem, QGraphicsTextItem
)
from PyQt6.QtGui import (
    QPainterPath, QPen, QBrush, QColor, QFont, QPainter
)
from PyQt6.QtCore import Qt, QPointF, QRectF

# --- 你的 FeynmanPlot 模块导入 ---
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    GluonLine, PhotonLine, WPlusLine, WMinusLine, ZBosonLine,
    FermionLine, AntiFermionLine, Line
)

# --- 自定义图形顶点类 ---
class GraphicsVertex(QGraphicsEllipseItem):
    def __init__(self, vertex_data: Vertex, radius: float = 0.5):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius) 
        self.vertex_data = vertex_data
        self.setPos(vertex_data.x, vertex_data.y)

        self.setBrush(QBrush(QColor(vertex_data.structured_facecolor if vertex_data.is_structured else "blue")))
        self.setPen(QPen(QColor(vertex_data.structured_edgecolor if vertex_data.is_structured else "darkblue"), 
                         vertex_data.structured_linewidth if vertex_data.is_structured else 1.0))

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.label_item = QGraphicsTextItem(vertex_data.label, parent=self)
        self.label_item.setFont(QFont("Times New Roman", 12))
        self.label_item.setDefaultTextColor(QColor("black")) 
        
        text_rect = self.label_item.boundingRect()
        label_x_offset = -text_rect.width() / 2 + vertex_data.label_offset[0]
        label_y_offset = -radius - text_rect.height() + vertex_data.label_offset[1]
        self.label_item.setPos(label_x_offset, label_y_offset)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.vertex_data.x = value.x()
            self.vertex_data.y = value.y()
            # 简化，暂不实现线条动态更新
            # 如果需要，可以在这里调用 self.scene().update_lines_connected_to(self.vertex_data)

        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
             if value:
                 if self.scene() and hasattr(self.scene(), '_main_window'):
                     self.scene()._main_window.show_properties_for(self.vertex_data)
             else:
                 if self.scene() and hasattr(self.scene(), '_main_window'):
                     self.scene()._main_window.clear_properties_panel()
        return super().itemChange(change, value)

# --- 自定义图形线条类 ---
class GraphicsLine(QGraphicsPathItem):
    def __init__(self, line_data: Line, start_vertex_item: 'GraphicsVertex', end_vertex_item: 'GraphicsVertex'):
        super().__init__()
        self.line_data = line_data
        self.start_vertex_item = start_vertex_item
        self.end_vertex_item = end_vertex_item

        plot_properties = self.line_data.get_plot_properties() 
        pen_color = QColor(plot_properties.get('color', 'black'))
        pen_width = plot_properties.get('linewidth', 1.0)
        
        linestyle_str = plot_properties.get('linestyle', '-')
        pen_style = Qt.PenStyle.SolidLine
        if linestyle_str == '--':
            pen_style = Qt.PenStyle.DashLine
        elif linestyle_str == '-.':
            pen_style = Qt.PenStyle.DashDotLine
        elif linestyle_str == ':':
            pen_style = Qt.PenStyle.DotLine

        self.setPen(QPen(pen_color, pen_width, pen_style))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        start_point = self.start_vertex_item.scenePos()
        end_point = self.end_vertex_item.scenePos()

        path.moveTo(start_point)
        path.lineTo(end_point)
        self.setPath(path)

        if self.line_data.label:
            for item in self.childItems():
                if isinstance(item, QGraphicsTextItem):
                    self.scene().removeItem(item)
            
            mid_point = (start_point + end_point) / 2
            label_item = QGraphicsTextItem(self.line_data.label, parent=self)
            
            label_properties = self.line_data.get_label_properties()
            label_item.setFont(QFont("Times New Roman", label_properties.get('fontsize', 10)))
            label_item.setDefaultTextColor(QColor(label_properties.get('color', "darkgray")))
            
            label_item.setPos(mid_point.x() + self.line_data.label_offset[0],
                              mid_point.y() + self.line_data.label_offset[1])

# --- 主应用程序窗口 ---
class FeynmanDiagramApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("费曼图绘制工具 (PyQt6 示例)")
        self.setGeometry(100, 100, 1200, 800)

        self.feynman_diagram = FeynmanDiagram()
        self.current_selected_item_data = None

        # --- Graphics View 和 Scene ---
        self.scene = QGraphicsScene(self)
        # 调整 sceneRect 初始大小以适应你的内容，这里扩大了一些
        self.scene.setSceneRect(-50, -50, 400, 300) 
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(self.view)

        self.scene._main_window = self 
        
        # --- 启用缩放和平移功能 ---
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag) # 启用手型工具拖拽场景
        self.view.wheelEvent = self.zoom_event # 覆盖 QGraphicsView 的 wheelEvent

        # --- 属性面板 (Dock Widget) ---
        self.property_dock = QDockWidget("属性", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_dock)
        self.property_panel_widget = QWidget()
        self.property_layout = QFormLayout(self.property_panel_widget)
        self.property_dock.setWidget(self.property_panel_widget)

        self.label_name = QLabel("名称:")
        self.input_name = QLineEdit()
        self.input_name.editingFinished.connect(self._update_selected_item_name)
        self.property_layout.addRow(self.label_name, self.input_name)

        # --- 控制按钮 (Dock Widget) ---
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        add_vertex_button = QPushButton("添加顶点")
        add_vertex_button.clicked.connect(self._add_test_vertex)
        control_layout.addWidget(add_vertex_button)

        add_line_button = QPushButton("添加线条 (v1 -> v2)")
        add_line_button.clicked.connect(self._add_test_line)
        control_layout.addWidget(add_line_button)

        draw_button = QPushButton("重新绘制所有")
        draw_button.clicked.connect(self._draw_diagram_in_scene)
        control_layout.addWidget(draw_button)

        control_dock = QDockWidget("控制", self)
        control_dock.setWidget(control_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, control_dock)

        # 初始数据和绘制
        self._initialize_diagram_data()
        self._draw_diagram_in_scene()

    # --- 新增的缩放事件处理方法 ---
    def zoom_event(self, event):
        """处理 QGraphicsView 的鼠标滚轮事件，用于缩放"""
        zoom_in_factor = 1.25 # 每次放大 25%
        zoom_out_factor = 1 / zoom_in_factor # 每次缩小相应比例

        # 获取鼠标滚轮的方向
        if event.angleDelta().y() > 0: # 向上滚动，放大
            factor = zoom_in_factor
        else: # 向下滚动，缩小
            factor = zoom_out_factor

        # 将缩放中心设置在鼠标光标位置
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # 执行缩放
        self.view.scale(factor, factor)

        # 恢复默认的缩放中心（可选，但在需要精确控制缩放中心时很重要）
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
    # --- 缩放事件处理方法结束 ---

    def _initialize_diagram_data(self):
        v1 = self.feynman_diagram.add_vertex(0, 0, label='A')
        v2 = self.feynman_diagram.add_vertex(50, 50, label='B') # 调整位置使初始图更大
        v_struct1 = self.feynman_diagram.add_vertex(
            -20, 20, label=r'Struct$_1$', is_structured=True, # 调整位置
            structured_radius=0.8, structured_facecolor='lightblue', label_offset=(0, 0.9),
            use_custom_hatch=True, custom_hatch_line_color='darkred', custom_hatch_line_width=1.0,
            custom_hatch_line_angle_deg=60, custom_hatch_spacing_ratio=0.08
        )
        
        self.feynman_diagram.add_line(v1, v2, GluonLine(label='g', line_plot_config={'color': 'purple', 'linewidth': 2.0}))
        self.feynman_diagram.add_line(v1, v_struct1, PhotonLine(label=r'$\gamma$', line_plot_config={'color': 'orange'}))

    def _add_vertex_to_scene(self, vertex_data: Vertex):
        graphics_vertex = GraphicsVertex(vertex_data, vertex_data.structured_radius if vertex_data.is_structured else 0.2)
        self.scene.addItem(graphics_vertex)

    def _draw_diagram_in_scene(self):
        self.scene.clear()

        vertex_item_map = {}
        for vertex_data in self.feynman_diagram.vertices:
            # 初始顶点大小可以调整，这里的 0.2 是半径，可以根据你的场景尺寸调整
            # 默认圆形半径可以更大，例如 5.0，这样初始显示就更大
            graphics_vertex = GraphicsVertex(vertex_data, 
                                             vertex_data.structured_radius if vertex_data.is_structured else 5.0) 
            self.scene.addItem(graphics_vertex)
            vertex_item_map[vertex_data] = graphics_vertex

        for line_data in self.feynman_diagram.lines:
            start_item = vertex_item_map.get(line_data.v_start)
            end_item = vertex_item_map.get(line_data.v_end)

            if start_item and end_item:
                graphics_line = GraphicsLine(line_data, start_item, end_item)
                self.scene.addItem(graphics_line)

        self.scene.update()

    def _add_test_vertex(self):
        # 调整随机生成顶点的范围，使其在更大的场景中更分散
        new_vertex = self.feynman_diagram.add_vertex(
            np.random.uniform(-40, 40), np.random.uniform(-40, 40), 
            label=f'V{len(self.feynman_diagram.vertices)}',
            color='purple'
        )
        self._add_vertex_to_scene(new_vertex)
        self.scene.update()

    def _add_test_line(self):
        if len(self.feynman_diagram.vertices) >= 2:
            v_start = self.feynman_diagram.vertices[0]
            v_end = self.feynman_diagram.vertices[1]
            
            self.feynman_diagram.add_line(v_start, v_end, FermionLine(label="Test Line", line_plot_config={'color': 'gray', 'linewidth': 1.0}))
            self._draw_diagram_in_scene()
        else:
            print("需要至少两个顶点才能添加测试线。")

    def show_properties_for(self, item_data):
        self.current_selected_item_data = item_data
        self.input_name.setText(item_data.label)
        self.property_dock.setWindowTitle(f"属性: {item_data.label}")

    def clear_properties_panel(self):
        self.current_selected_item_data = None
        self.input_name.clear()
        self.property_dock.setWindowTitle("属性")

    def _update_selected_item_name(self):
        if self.current_selected_item_data:
            self.current_selected_item_data.label = self.input_name.text()
            self._draw_diagram_in_scene()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FeynmanDiagramApp()
    window.show()
    sys.exit(app.exec())