class ToolboxController:
    def __init__(self, toolbox_widget):
        self.toolbox = toolbox_widget
        self.setup_buttons()

    def setup_buttons(self):
        self.toolbox.add_button.clicked.connect(self.on_add)

    def on_add(self):
        # 调用 canvas_controller 的接口（通过 MainController 协调）
        pass

    def update(self):
        # 刷新工具按钮状态
        pass
