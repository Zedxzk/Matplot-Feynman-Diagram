class NavbarController:
    def __init__(self, navbar_widget):
        self.navbar = navbar_widget
        self.setup_connections()

    def setup_connections(self):
        self.navbar.save_button.clicked.connect(self.on_save)
        self.navbar.open_button.clicked.connect(self.on_open)

    def on_save(self):
        # 处理保存逻辑
        pass

    def update(self):
        # 更新状态，比如是否可用
        pass
