from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
)

class AddLineDialog(QDialog):
    def __init__(self, vertices, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加费曼图线条")

        self.vertices = vertices

        layout = QVBoxLayout()

        # 顶点1下拉菜单
        layout.addWidget(QLabel("选择起点顶点"))
        self.vertex1_combo = QComboBox()
        for i, v in enumerate(vertices):
            label = v.label if hasattr(v, 'label') else f"顶点{i}"
            self.vertex1_combo.addItem(label, v)
        layout.addWidget(self.vertex1_combo)

        # 顶点2下拉菜单
        layout.addWidget(QLabel("选择终点顶点"))
        self.vertex2_combo = QComboBox()
        for i, v in enumerate(vertices):
            label = v.label if hasattr(v, 'label') else f"顶点{i}"
            self.vertex2_combo.addItem(label, v)
        layout.addWidget(self.vertex2_combo)

        # 粒子类型下拉菜单
        layout.addWidget(QLabel("选择粒子类型"))
        self.particle_type_combo = QComboBox()
        self.particle_type_combo.addItems(["费米子", "反费米子", "光子", "胶子", "W+", "W-", "Z玻色子"])
        layout.addWidget(self.particle_type_combo)

        # 按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        self.ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 连接信号，监听选择变化
        self.vertex1_combo.currentIndexChanged.connect(self.on_selection_changed)
        self.vertex2_combo.currentIndexChanged.connect(self.on_selection_changed)
        self.particle_type_combo.currentIndexChanged.connect(self.on_selection_changed)

        # 初次更新按钮状态
        self.on_selection_changed()

    def on_selection_changed(self):
        v_start = self.vertex1_combo.currentData()
        v_end = self.vertex2_combo.currentData()
        particle_type = self.particle_type_combo.currentText()

        print(f"当前选择：起点={v_start}, 终点={v_end}, 粒子类型={particle_type}")

        # 禁止起点和终点相同
        if v_start == v_end:
            self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(True)
    
        # 强制刷新界面
        self.update()  # 或者 self.repaint()

    def get_selected_data(self):
        v_start = self.vertex1_combo.currentData()
        v_end = self.vertex2_combo.currentData()
        particle_type = self.particle_type_combo.currentText()
        return v_start, v_end, particle_type
