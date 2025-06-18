# feynplot_GUI/feynplot_gui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QMenu, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from feynplot_GUI.feynplot_gui.canvas_widget import CanvasWidget
from feynplot_GUI.feynplot_gui.controller import Controller
from feynplot.core.diagram import FeynmanDiagram

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FeynPlot GUI")
        self.setGeometry(100, 100, 1200, 800)

        self._create_widgets()
        self._create_layouts()
        
        self.ctrl = Controller(
            self.canvas,
            self.vertex_list_widget,
            self.line_list_widget
        )
        self.ctrl.main_window = self

        self._create_menu_bar()
        # self.ctrl.item_manager.update_list_widgets() # <-- 添加这一行

    def _create_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.canvas = CanvasWidget(parent=self.central_widget)

        self.vertex_list_widget = QListWidget()
        self.vertex_list_widget.setWindowTitle("Vertices")
        self.vertex_list_widget.setSelectionMode(QListWidget.SingleSelection)

        self.line_list_widget = QListWidget()
        self.line_list_widget.setWindowTitle("Lines")
        self.line_list_widget.setSelectionMode(QListWidget.SingleSelection)

    def _create_layouts(self):
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.vertex_list_widget)
        left_layout.addWidget(self.line_list_widget)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(self.canvas, 4)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("文件")
        
        new_action = QAction("新建", self)
        new_action.triggered.connect(self._new_diagram)
        file_menu.addAction(new_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("编辑")
        add_vertex_action = QAction("添加顶点...", self)
        add_vertex_action.triggered.connect(lambda: self.ctrl.item_manager.add_new_vertex_at_coords(0, 0))
        edit_menu.addAction(add_vertex_action)
        
        add_line_action = QAction("添加线条...", self)
        add_line_action.triggered.connect(self.ctrl.item_manager.start_add_line_process)
        edit_menu.addAction(add_line_action)

        help_menu = menu_bar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _new_diagram(self):
        reply = QMessageBox.question(self, '新建',
                                     "您确定要新建一个图表吗？这将清除当前所有数据。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ctrl.diagram_model = FeynmanDiagram()
            self.ctrl.initialize_diagram_data()

    def _show_about_dialog(self):
        QMessageBox.about(self, "关于 FeynPlot GUI",
                          "这是一个用于绘制费曼图的简单GUI应用。\n"
                          "版本: 1.0\n"
                          "作者: ZED")