# feynplot_gui/widgets/vertex_list_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Signal, Qt # 导入 Qt 用于 ItemDataRole

class VertexListWidget(QListWidget):
    """
    一个专门用于显示图中顶点列表的 QListWidget。
    可以发出信号，通知控制器用户交互。
    """
    # 信号：当一个顶点被选中时发出，传递选中的 Vertex 对象
    vertex_selected = Signal(object)
    # 信号：当一个顶点被双击时发出，传递双击的 Vertex 对象
    vertex_double_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("顶点列表")
        self.setFixedWidth(200) # 可以设置一个默认宽度

        # 连接内置信号到自定义槽函数
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_selection_changed(self):
        """处理列表项选择变化的槽函数。"""
        selected_items = self.selectedItems()
        if selected_items:
            # 获取存储在 ItemDataRole.UserRole 中的实际 Vertex 对象
            vertex = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.vertex_selected.emit(vertex)
        else:
            self.vertex_selected.emit(None) # 没有选中项时发出 None

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击的槽函数。"""
        vertex = item.data(Qt.ItemDataRole.UserRole)
        if vertex:
            self.vertex_double_clicked.emit(vertex)

    def add_vertex_item(self, vertex_data):
        """
        向列表中添加一个顶点项。
        Args:
            vertex_data: 实际的 Vertex 对象。
        """
        item_text = f"[{vertex_data.id}] Vtx: {vertex_data.label} ({vertex_data.x:.2f}, {vertex_data.y:.2f})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, vertex_data) # 将 Vertex 对象存储在用户数据中
        self.addItem(item)

    def clear_list(self):
        """清空列表中的所有项。"""
        self.clear()

    def get_selected_vertex(self):
        """获取当前选中的 Vertex 对象，如果没有选中则返回 None。"""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None

# 如果需要测试，可以添加以下代码
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
    from feynplot.core.vertex import Vertex, VertexType # 假设你的 Vertex 类路径是这个

    class MockVertex(Vertex):
        # 模拟 Vertex 类，因为 feynplot.core.vertex 外部不可用
        def __init__(self, x, y, label="V", id_val=None, vertex_type=VertexType.GENERIC):
            self.x = x
            self.y = y
            self.label = label
            self.id = id_val if id_val else f"vtx_{id(self)}"
            self.vertex_type = vertex_type

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("VertexListWidget Test")
            self.setGeometry(100, 100, 400, 300)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            self.vertex_list = VertexListWidget()
            layout.addWidget(self.vertex_list)

            # 添加一些模拟数据
            v1 = MockVertex(10, 20, "Electron", "v1")
            v2 = MockVertex(50, 60, "Photon", "v2", VertexType.PHOTON)
            self.vertex_list.add_vertex_item(v1)
            self.vertex_list.add_vertex_item(v2)

            self.vertex_list.vertex_selected.connect(lambda v: print(f"Selected: {v.id if v else 'None'}"))
            self.vertex_list.vertex_double_clicked.connect(lambda v: print(f"Double Clicked: {v.id}"))

    app = QApplication([])
    window = TestWindow()
    window.show()
    app.exec()