# feynplot_gui/widgets/line_list_widget.py

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Signal, Qt # 导入 Qt 用于 ItemDataRole

class LineListWidget(QListWidget):
    """
    一个专门用于显示图中线条列表的 QListWidget。
    可以发出信号，通知控制器用户交互。
    """
    # 信号：当一条线条被选中时发出，传递选中的 Line 对象
    line_selected = Signal(object)
    # 信号：当一条线条被双击时发出，传递双击的 Line 对象
    line_double_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("线条列表")
        self.setFixedWidth(200) # 可以设置一个默认宽度

        # 连接内置信号到自定义槽函数
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_selection_changed(self):
        """处理列表项选择变化的槽函数。"""
        selected_items = self.selectedItems()
        if selected_items:
            # 获取存储在 ItemDataRole.UserRole 中的实际 Line 对象
            line = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.line_selected.emit(line)
        else:
            self.line_selected.emit(None) # 没有选中项时发出 None

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击的槽函数。"""
        line = item.data(Qt.ItemDataRole.UserRole)
        if line:
            self.line_double_clicked.emit(line)

    def add_line_item(self, line_data):
        """
        向列表中添加一个线条项。
        Args:
            line_data: 实际的 Line 对象。
        """
        # 假设 line_data 有 v_start 和 v_end 属性，它们也是 Vertex 对象
        start_label = line_data.v_start.label if line_data.v_start else "None"
        end_label = line_data.v_end.label if line_data.v_end else "None"
        item_text = f"[{line_data.id}] Line: {line_data.label} ({start_label} -> {end_label})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, line_data) # 将 Line 对象存储在用户数据中
        self.addItem(item)

    def clear_list(self):
        """清空列表中的所有项。"""
        self.clear()

    def get_selected_line(self):
        """获取当前选中的 Line 对象，如果没有选中则返回 None。"""
        selected_items = self.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None

# 如果需要测试，可以添加以下代码
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
    from feynplot.core.line import Line, LineStyle, FermionLine # 假设你的 Line 类路径是这个
    from feynplot.core.vertex import Vertex, VertexType # 还需要 Vertex 来模拟 Line 的端点

    # 模拟 Vertex 和 Line 类
    class MockVertex:
        def __init__(self, x, y, label="V", id_val=None):
            self.x = x
            self.y = y
            self.label = label
            self.id = id_val if id_val else f"vtx_{id(self)}"

    class MockLine:
        def __init__(self, v_start, v_end, label="Line", id_val=None, line_type=LineStyle.SOLID):
            self.v_start = v_start
            self.v_end = v_end
            self.label = label
            self.id = id_val if id_val else f"line_{id(self)}"
            self.line_type = line_type

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("LineListWidget Test")
            self.setGeometry(100, 100, 400, 300)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            self.line_list = LineListWidget()
            layout.addWidget(self.line_list)

            # 添加一些模拟数据
            v1 = MockVertex(10, 20, "V1", "v1")
            v2 = MockVertex(50, 60, "V2", "v2")
            v3 = MockVertex(80, 90, "V3", "v3")

            l1 = MockLine(v1, v2, "Electron Line", "l1", LineStyle.FERMION)
            l2 = MockLine(v2, v3, "Photon Line", "l2", LineStyle.PHOTON)
            self.line_list.add_line_item(l1)
            self.line_list.add_line_item(l2)

            self.line_list.line_selected.connect(lambda l: print(f"Selected: {l.id if l else 'None'}"))
            self.line_list.line_double_clicked.connect(lambda l: print(f"Double Clicked: {l.id}"))

    app = QApplication([])
    window = TestWindow()
    window.show()
    app.exec()