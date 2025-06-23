# gui/mainwindow.py
import numpy as np

from PyQt6.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QWidget, QPushButton, QDockWidget, QLabel, QLineEdit, QFormLayout,
)
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt, QPointF, QRectF

# 导入核心 feynplot 模块
from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    GluonLine, PhotonLine, WPlusLine, WMinusLine, ZBosonLine,
    FermionLine, AntiFermionLine, Line
)

# 导入自定义部件
from .widgets.property_panel import PropertyPanel  # 导入 PropertyPanel

# 导入控制器
from .controllers.diagram_controller import DiagramController # 导入 DiagramController

class FeynmanDiagramApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("费曼图绘制工具 (PyQt6 示例)")
        self.setGeometry(100, 100, 1200, 800)

        # 初始化费曼图数据模型
        self.feynman_diagram = FeynmanDiagram()

        # --- Graphics View 和 Scene 设置 ---
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-50, -50, 400, 300) 
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # 开启抗锯齿
        self.setCentralWidget(self.view)

        # 实例化 DiagramController，并将核心组件传递给它
        self.diagram_controller = DiagramController(self.feynman_diagram, self.scene, self.view)
        
        # 将 DiagramController 实例存储在场景中，以便 GraphicsItem 可以访问它来触发更新
        self.scene._diagram_controller = self.diagram_controller
        # 仍然保留对主窗口的引用，以防 GraphicsItem 需要直接访问主窗口的特定方法
        self.scene._main_window = self 

        # --- 启用缩放和平移 ---
        # 设置拖拽模式为滚动（平移）
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # 将滚轮事件连接到控制器中的缩放方法
        self.view.wheelEvent = self.diagram_controller.zoom_event 
        # 监听场景中选中项的变化，并连接到本地槽函数
        self.scene.selectionChanged.connect(self._on_selection_changed)


        # --- 属性面板 (停靠部件) ---
        self.property_dock = QDockWidget("属性", self)
        # 将停靠部件放置在右侧
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_dock)
        
        # 实例化自定义的 PropertyPanel 部件
        self.property_panel = PropertyPanel() 
        self.property_dock.setWidget(self.property_panel)

        # 将属性面板中名称输入框的 'editingFinished' 信号连接到本地槽函数
        # 当用户完成名称编辑时，会触发这个信号
        self.property_panel.name_input.editingFinished.connect(self._update_selected_item_name_from_panel)


        # --- 控制按钮 (停靠部件) ---
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # 添加顶点按钮
        add_vertex_button = QPushButton("添加顶点")
        # 按钮点击事件连接到控制器的方法
        add_vertex_button.clicked.connect(self.diagram_controller.add_test_vertex)
        control_layout.addWidget(add_vertex_button)

        # 添加线条按钮
        add_line_button = QPushButton("添加线条 (v1 -> v2)")
        # 按钮点击事件连接到控制器的方法
        add_line_button.clicked.connect(self.diagram_controller.add_test_line)
        control_layout.addWidget(add_line_button)

        # 重新绘制所有按钮
        draw_button = QPushButton("重新绘制所有")
        # 按钮点击事件连接到控制器的方法
        draw_button.clicked.connect(self.diagram_controller.draw_diagram_in_scene)
        control_layout.addWidget(draw_button)

        # 将控制按钮部件放置在左侧停靠部件中
        control_dock = QDockWidget("控制", self)
        control_dock.setWidget(control_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, control_dock)

        # 应用程序启动时，初始化图数据并绘制
        self.diagram_controller.initialize_diagram_data()
        self.diagram_controller.draw_diagram_in_scene()

                # 👇 添加这些代码来自动设置合适的 sceneRect 和初始缩放
        bounding_rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(bounding_rect)
        self.view.fitInView(bounding_rect, Qt.AspectRatioMode.KeepAspectRatio)

    # --- 私有槽函数，用于处理来自 UI 或控制器的信号 ---

    def _on_selection_changed(self):
        """
        当 QGraphicsScene 中的选中项发生变化时调用。
        此函数会更新属性面板以显示选中项的属性。
        """
        selected_items = self.scene.selectedItems()
        if selected_items:
            # 假设只处理单个选中项，或者只处理第一个选中项
            selected_graphics_item = selected_items[0]
            # 从控制器获取选中图形项对应的底层数据模型对象
            item_data = self.diagram_controller.get_selected_item_data(selected_graphics_item)
            if item_data:
                # 更新属性面板的显示
                self.property_panel.update_properties(item_data)
                # 更新属性停靠部件的标题
                self.property_dock.setWindowTitle(f"属性: {item_data.label}")
            else:
                # 如果获取不到数据（例如选中了非自定义图形项），则清空属性面板
                self.property_panel.clear_properties()
                self.property_dock.setWindowTitle("属性")
        else:
            # 如果没有选中任何项，则清空属性面板
            self.property_panel.clear_properties()
            self.property_dock.setWindowTitle("属性")

    def _update_selected_item_name_from_panel(self):
        """
        当属性面板中名称输入框的编辑完成时调用。
        此函数会通知控制器更新数据模型的标签。
        """
        # 从 PropertyPanel 获取当前正在编辑的数据模型对象
        current_data = self.property_panel.current_item_data 
        if current_data:
            new_name = self.property_panel.name_input.text()
            # 调用控制器的方法来更新数据模型的标签，并同步到图形项
            self.diagram_controller.update_item_label(current_data, new_name)
            # 更新属性停靠部件的标题
            self.property_dock.setWindowTitle(f"属性: {new_name}") 
            # 注意：`update_item_label` 内部已经处理了图形项标签的更新，
            # 这里不需要 `self.diagram_controller.draw_diagram_in_scene()` 全量重绘。