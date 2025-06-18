# feynplot_gui/controllers/toolbox_controller.py

from PySide6.QtCore import QObject, Signal # 导入 QObject 和 Signal

# 导入 UI Widget
from feynplot_gui.widgets.toolbox_widget import ToolboxWidget # 确保这是正确的导入路径

# 【重要修改】移除对 MainController 的直接导入，以避免循环导入
# from feynplot_gui.controllers.main_controller import MainController

class ToolboxController(QObject): # 继承自 QObject
    # 这个信号用于通知MainController当前UI上的选中/激活状态，
    # 例如，如果toolbox有radio button来表示当前是选择工具还是添加工具。
    # 如果你的toolbox只有动作按钮，则可能不需要这个信号。
    # tool_mode_changed = Signal(str)

    def __init__(self, toolbox_widget: ToolboxWidget, main_controller: 'MainController'): # 修正后的签名和类型提示
        super().__init__() # 调用 QObject 的构造函数

        self.toolbox_widget = toolbox_widget
        self.main_controller = main_controller # 保存 MainController 的引用

        self.setup_buttons()

    def setup_buttons(self):
        """连接工具箱按钮的信号到 MainController 的相应方法。"""
        
        # 直接将 ToolboxWidget 的具体操作信号连接到 MainController 的对应方法
        # 注意：这里的信号名称必须与你的 ToolboxWidget 中实际定义的信号名称完全一致

        # 添加操作
        # 注意：这里的 add_vertex_requested 和 add_line_requested 信号，
        # 如果你希望通过点击这些按钮直接触发 MainController 进入“添加顶点/线条模式”
        # 那么它们应该连接到 MainController.set_current_tool_mode 方法，
        # 而不是直接触发添加对话框。
        # 我先假设你希望它们切换模式。
        # self.toolbox_widget.add_vertex_requested.connect(
            # lambda: self.main_controller.set_current_tool_mode('add_vertex')
        # )
        # self.toolbox_widget.add_line_requested.connect(
        #     lambda: self.main_controller.set_current_tool_mode('add_line')
        # )

        # 删除操作
        # 这里假设 delete_vertex_requested 和 delete_line_requested 信号代表删除请求
        # 我们可以将它们连接到 MainController 的统一删除方法
        self.toolbox_widget.delete_vertex_requested.connect(self.main_controller.delete_selected_object)
        self.toolbox_widget.delete_line_requested.connect(self.main_controller.delete_selected_object)
        
        # 撤销/重做
        # self.toolbox_widget.undo_action_requested.connect(self.main_controller.undo)
        # self.toolbox_widget.redo_action_requested.connect(self.main_controller.redo)

        # 保存（如果工具箱中有保存按钮，导航栏通常也有）
        self.toolbox_widget.save_diagram_requested.connect(self.main_controller.save_diagram_to_file)

        # 清空图（如果需要确认，MainController 来处理确认逻辑）
        # 如果 _on_clear_diagram_button_clicked 最终是触发一个信号，可以直接连接
        # 否则，你需要修改 ToolboxWidget 让其发出一个信号
        # 假设 ToolboxWidget 会发出一个 clear_diagram_requested 信号
        # self.toolbox_widget.clear_diagram_button.clicked.connect(self.main_controller.clear_diagram)
        # 假设 ToolboxWidget 内部处理确认并发出了一个清空图的信号
        self.toolbox_widget.clear_diagram_requested.connect(self.main_controller.clear_diagram)


    def update_tool_mode(self, mode: str):
        """
        根据 MainController 传递的当前工具模式更新工具箱按钮的选中状态。
        如果你的工具箱按钮是可切换状态的 (比如 QToolButton 的 checkable 属性)，
        你可以在这里设置哪个按钮是“选中”的。
        例如：
        if mode == 'select':
            self.toolbox_widget.selection_tool_button.setChecked(True)
        elif mode == 'add_vertex':
            self.toolbox_widget.add_vertex_button.setChecked(True)
        # ...
        """
        # 你需要根据实际的 ToolboxWidget 控件来编写这里的逻辑
        # 例如，如果你的按钮有 setChecked 方法
        if hasattr(self.toolbox_widget, 'add_vertex_button') and mode == 'add_vertex':
            self.toolbox_widget.add_vertex_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'add_line_button') and mode == 'add_line':
            self.toolbox_widget.add_line_button.setChecked(True)
        # 假设你有一个默认的选择工具按钮，当不是添加模式时选中它
        elif hasattr(self.toolbox_widget, 'selection_button') and mode == 'select':
             self.toolbox_widget.selection_button.setChecked(True)
        else:
             # 确保其他按钮都是未选中状态
             if hasattr(self.toolbox_widget, 'add_vertex_button'): self.toolbox_widget.add_vertex_button.setChecked(False)
             if hasattr(self.toolbox_widget, 'add_line_button'): self.toolbox_widget.add_line_button.setChecked(False)
             if hasattr(self.toolbox_widget, 'selection_button'): self.toolbox_widget.selection_button.setChecked(False)
             
        self.main_controller.status_message.emit(f"工具箱工具模式已更新为：{mode}")


    def update(self):
        """通用的更新方法，目前不需要额外逻辑。"""
        pass