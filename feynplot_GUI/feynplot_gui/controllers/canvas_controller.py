class CanvasController:
    def __init__(self, canvas_widget):
        self.canvas = canvas_widget
        self.object_panel_controller = None

    def set_object_panel_controller(self, controller):
        self.object_panel_controller = controller

    def add_item(self, item):
        self.canvas.add(item)
        if self.object_panel_controller:
            self.object_panel_controller.refresh()

    def update(self):
        self.canvas.repaint()
