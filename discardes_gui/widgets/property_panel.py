# gui/widgets/property_panel.py
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QObject 

class PropertyPanel(QWidget):
    """
    用于显示和编辑选中图形项属性的面板部件。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self) # 主布局
        self.form_layout = QFormLayout() # 表单布局用于显示属性字段
        self.layout.addLayout(self.form_layout)
        
        # 存储当前属性面板显示的数据模型对象
        self.current_item_data: Optional[Any] = None 

        # 示例：名称字段 (所有可编辑项都可能有的通用属性)
        self.name_label = QLabel("名称:")
        self.name_input = QLineEdit()
        self.form_layout.addRow(self.name_label, self.name_input)
        # 注意：name_input 的信号连接在 mainwindow.py 中处理，
        # 因为主窗口需要协调 PropertyPanel 和 DiagramController。

    def update_properties(self, item_data: Any):
        """
        根据传入的数据模型对象更新属性面板的显示。
        """
        self.current_item_data = item_data # 更新当前关联的数据对象
        if item_data:
            # 首先清空所有字段，以防显示的是旧数据
            self.clear_properties() 
            # 如果数据对象有 'label' 属性，则填充名称输入框
            if hasattr(item_data, 'label'):
                self.name_input.setText(item_data.label)
            
            # TODO: 在这里添加更多字段和逻辑，根据 item_data 的具体类型
            # (例如，Vertex 或 Line) 来动态显示或隐藏不同的属性字段。
            # 例如：
            # if isinstance(item_data, Vertex):
            #     # 添加或显示顶点特有的属性输入框（如类型、颜色等）
            #     pass
            # elif isinstance(item_data, Line):
            #     # 添加或显示线条特有的属性输入框（如线条类型、宽度、样式等）
            #     pass
        else:
            # 如果传入 None，则清空属性面板
            self.clear_properties()

    def clear_properties(self):
        """
        清空属性面板中的所有字段。
        """
        self.current_item_data = None # 清除当前关联的数据对象
        self.name_input.clear() # 清空名称输入框
        # TODO: 清空其他可能存在的属性输入框