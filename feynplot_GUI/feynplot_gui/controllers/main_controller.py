from .canvas_controller import CanvasController
from .navigation_bar_controller import NavbarController
from .toolbox_controller import ToolboxController
from .vertex_controller import VertexController
from .line_controller import LineController

class MainController:
    def __init__(self, main_window):
        self.main_window = main_window

        self.navbar_controller  = NavbarController(main_window.navbar)
        self.canvas_controller  = CanvasController(main_window.canvas)
        self.vertex_controller  = VertexController(main_window.vertex_panel)
        self.line_controller    = LineController(main_window.line_panel)
        self.toolbox_controller = ToolboxController(main_window.toolbox)

        self._link_controllers()

    def _link_controllers(self):
        # 举例：canvas_controller 可以调用 vertex_controller 方法
        self.canvas_controller.set_vertex_controller(self.vertex_controller)
        # 其它控制器之间链接

    def update_all(self):
        self.navbar_controller.update()
        self.canvas_controller.update()
        self.vertex_controller.update()
        self.line_controller.update()
        self.toolbox_controller.update()
