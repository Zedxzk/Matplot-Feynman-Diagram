# feynplot_gui\core_ui\controllers\other_texts_controller.py

from PySide6.QtWidgets import QMessageBox, QInputDialog, QWidget
from PySide6.QtCore import Qt, QObject, Signal
from feynplot_gui.debug.debug_output import other_texts_print # 假设这是你的调试输出函数

# 导入真正的 MainController
# 假设你的 MainController 在 feynplot_gui.core_ui.controllers.main_controller 模块中
# 注意：这里我们只进行类型导入，避免循环依赖在运行时发生
# 你需要确保 MainController 类中包含了 get_selected_item() 和 select_item() 方法，
# 以及 main_window 和 canvas_controller 属性。
# from feynplot_gui.core_ui.controllers.main_controller import MainController as RealMainController

# 你的 TextElement 类定义
class TextElement:
    _next_id = 1
    def __init__(self, text: str, x: float = 0.0, y: float = 0.0):
        self.id = TextElement._next_id
        TextElement._next_id += 1
        self.text = text
        self.x = x
        self.y = y
        self.is_selected = False # 用于UI同步选择状态

    def __repr__(self):
        return f"TextElement(id={self.id}, text='{self.text}', x={self.x}, y={self.y})"

# 导入 UI Widgets
from feynplot_gui.core_ui.widgets.other_texts_widget import OtherTextsWidget

# 仅用于类型提示的 MainController 桩 (Stub) 类
# 这是一个临时的定义，帮助 Pylance 进行静态分析。
# 实际运行时会使用真正导入的 MainController。
class MainController:
    status_message: Signal = Signal(str)
    project_root: str
    main_window: QWidget # MainController应该持有MainWindow的引用
    
    # 模拟 MainController 中的 CanvasController 结构，用于类型提示
    class CanvasControllerMock:
        canvas_widget: QWidget = None
        def update_canvas(self): pass
    canvas_controller: CanvasControllerMock = CanvasControllerMock()

    def get_selected_item(self) -> object: pass # 声明 get_selected_item 方法
    def select_item(self, item: object): pass # 声明 select_item 方法
    def update_all_views(self): pass # 声明 update_all_views 方法


class OtherTextsController(QObject):
    """
    Controller for the OtherTextsWidget, managing interactions related to TextElement objects.
    These text elements are considered private to this controller and not part of the core diagram model.
    """
    def __init__(self, other_texts_widget: OtherTextsWidget, main_controller: "MainController"):
        super().__init__()

        self.other_texts_widget = other_texts_widget
        self.main_controller = main_controller

        self.text_elements = [] # <-- 文本元素现在由 OtherTextsController 私有管理

        self.setup_connections()
        self.update_text_list() # 初始填充列表

    def setup_connections(self):
        """连接 OtherTextsWidget 信号到本控制器的槽函数。"""
        other_texts_print("设置连接中...")
        self.other_texts_widget.text_selected.connect(self._on_text_list_selected)
        self.other_texts_widget.text_double_clicked.connect(self._on_text_list_double_clicked)
        self.other_texts_widget.list_blank_clicked.connect(self._on_text_list_blank_clicked)
        
        self.other_texts_widget.edit_text_requested.connect(self._on_request_edit_text)
        self.other_texts_widget.delete_text_requested.connect(self._on_request_delete_text)
        self.other_texts_widget.add_new_text_requested.connect(self._on_request_add_new_text)
        other_texts_print("连接设置完毕。")

    def update_text_list(self):
        """
        根据本控制器私有的 text_elements 刷新文本列表视图。
        文本按其唯一标识符 (ID) 升序排序。
        """
        other_texts_print("从私有集合更新文本列表中...")
        self.other_texts_widget.blockSignals(True) 

        self.other_texts_widget.clear_list()

        sorted_texts = sorted(self.text_elements, key=lambda text: text.id) # 从私有列表获取

        for text_elem in sorted_texts:
            self.other_texts_widget.add_text_item(text_elem) 

            # 如果当前有全局选中项，且是这个文本，则同步视图
            # 注意：这里直接访问 self.main_controller.selected_item 假设 MainController 在外部已正确处理选择逻辑
            # 最佳实践是 MainController 应该有一个 get_selected_item() 方法来获取当前选中项
            if self.main_controller.get_selected_item() is text_elem: # 使用 get_selected_item()
                 self.other_texts_widget.set_selected_item_in_list(text_elem)

        self.other_texts_widget.blockSignals(False) 
        self.main_controller.status_message.emit("文本列表已更新并按ID排序。")
        other_texts_print("文本列表已从私有集合更新。")

    def set_selected_item_in_list(self, item: [TextElement, None]):
        """
        接收来自 MainController 的选中项，并在文本列表中设置/清除选中状态。
        """
        self.other_texts_widget.set_selected_item_in_list(item)

    # --- 槽函数：响应 OtherTextsWidget 信号 ---

    def _on_text_list_selected(self, text_element: TextElement):
        """
        当用户在列表中选择一个文本元素时触发。
        通知 MainController 管理全局选择状态。
        """
        if text_element:
            other_texts_print(f"文本 {text_element.id} 在列表中选中。")
            current_global_selection = self.main_controller.get_selected_item() # 使用 get_selected_item()
            
            # 如果当前全局选中项不是此文本元素，则选中此文本元素
            if current_global_selection is not text_element:
                self.main_controller.select_item(text_element)
        else:
            other_texts_print("文本列表选择已清除。")
            # 当列表选择被清除时，如果全局选中项是文本，则清除全局选中
            if isinstance(self.main_controller.get_selected_item(), TextElement): # 使用 get_selected_item()
                self.main_controller.select_item(None)

    def _on_text_list_double_clicked(self, text_element: TextElement):
        """
        当用户双击列表中一个文本元素时触发。
        直接打开编辑对话框。
        """
        other_texts_print(f"文本 {text_element.id} 在列表中双击。请求编辑。")
        self._on_request_edit_text(text_element)

    def _on_text_list_blank_clicked(self):
        """
        当文本列表的空白区域被点击时触发。
        如果选中项是文本元素，则通知 MainController 清除全局选中。
        """
        other_texts_print("文本列表空白区域被点击。")
        # 这里你可以选择是否清除全局选中。如果你希望点击空白区域就清除，保留下面一行。
        # 如果你希望只有在选中文本时才清除，则需要额外判断。
        if isinstance(self.main_controller.get_selected_item(), TextElement): # 使用 get_selected_item()
            self.main_controller.select_item(None)

    # --- 新增槽函数：响应上下文菜单和添加请求 ---

    def _on_request_edit_text(self, text_element: TextElement):
        """
        处理“编辑文本”请求。直接在此控制器的私有集合中编辑文本。
        """
        other_texts_print(f"收到编辑文本请求，ID：{text_element.id}")
        self.main_controller.status_message.emit(f"打开文本编辑对话框：{text_element.id}")
        
        parent_widget = self.main_controller.main_window # 使用实际的 MainWindow 实例作为父级

        new_text_content, ok = QInputDialog.getText(parent_widget,
                                                     f"编辑文本 {text_element.id}", 
                                                     "请输入新文本内容:", 
                                                     text=text_element.text)
        if ok and new_text_content is not None:
            text_element.text = new_text_content # 更新私有模型数据
            # 如果需要更新X, Y坐标，可以在这里加入逻辑
            
            self.update_text_list() # 更新自己的视图
            self.main_controller.status_message.emit(f"成功编辑文本：{text_element.id}")
            self.set_selected_item_in_list(text_element) # 重新选中编辑的文本
            # 通知 MainController 更新画布，因为文本显示可能已更改
            self.main_controller.canvas_controller.update_canvas() # <--- 通知画布重绘
            other_texts_print(f"文本 {text_element.id} 更新为 '{text_element.text}'。")
        else:
            self.main_controller.status_message.emit(f"文本 {text_element.id} 编辑已取消。")
            other_texts_print(f"文本 {text_element.id} 编辑已取消。")

    def _on_request_delete_text(self, text_element: TextElement):
        """
        处理“删除文本”请求。直接在此控制器的私有集合中删除文本。
        """
        other_texts_print(f"收到删除文本请求，ID：{text_element.id}")
        self.main_controller.status_message.emit(f"收到删除文本请求：{text_element.id} (自行处理)")
        
        reply = QMessageBox.question(self.main_controller.main_window, '确认删除文本', 
                                     f"确定要删除文本 '{text_element.text}' (ID: {text_element.id}) 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.text_elements = [t for t in self.text_elements if t.id != text_element.id] # 从私有列表移除

            if self.main_controller.get_selected_item() is text_element: # 如果删除的是当前选中项，则清除全局选中
                self.main_controller.select_item(None)
            
            self.update_text_list() # 更新自己的视图
            # 通知 MainController 更新画布，因为文本将被移除
            self.main_controller.canvas_controller.update_canvas() # <--- 通知画布重绘
            self.main_controller.status_message.emit(f"文本 {text_element.id} 已删除。")
            other_texts_print(f"文本 {text_element.id} 已从私有集合中删除。")
        else:
            self.main_controller.status_message.emit("删除文本操作已取消。")
            other_texts_print("删除文本操作已取消。")

    def _on_request_add_new_text(self):
        """
        处理“添加新文本”请求。直接在此控制器的私有集合中添加新文本。
        """
        other_texts_print("收到添加新文本请求。")
        self.main_controller.status_message.emit("打开添加新文本对话框。")

        parent_widget = self.main_controller.main_window # 使用实际的 MainWindow 实例作为父级

        new_text_content, ok = QInputDialog.getText(parent_widget,
                                                     "添加新文本", 
                                                     "请输入新文本内容:")
        if ok and new_text_content:
            new_text_elem = TextElement(text=new_text_content, x=0, y=0) 
            self.text_elements.append(new_text_elem) 
            
            self.update_text_list() 
            self.main_controller.select_item(new_text_elem) 
            # 通知 MainController 更新画布，因为添加了新文本
            self.main_controller.canvas_controller.update_canvas() # <--- 通知画布重绘
            self.main_controller.status_message.emit(f"成功添加新文本：{new_text_elem.id}")
            other_texts_print(f"新文本已添加到私有集合：{new_text_elem}")
        else:
            self.main_controller.status_message.emit("添加新文本操作已取消。")
            other_texts_print("添加新文本操作已取消。")

    def update(self):
        """一个通用的更新方法，在需要时由 MainController 调用。"""
        self.update_text_list()

    # 新增方法: 绘制文本到Matplotlib画布
    def draw_texts_on_canvas(self, ax):
        """
        将此控制器管理的文本元素绘制到给定的 Matplotlib 轴上。
        
        Args:
            ax (matplotlib.axes.Axes): 用于绘制的 Matplotlib 轴对象。
        """
        other_texts_print("在画布上绘制文本元素。")
        for text_elem in self.text_elements:
            color = 'red' if text_elem.is_selected else 'black'
            font_weight = 'bold' if text_elem.is_selected else 'normal'
            # 根据你的图表布局调整位置和对齐方式
            ax.text(text_elem.x, text_elem.y, text_elem.text,
                    color=color, fontsize=20, fontweight=font_weight,
                    ha='center', va='center', clip_on=True) # clip_on=True 确保文本保持在轴边界内
        other_texts_print(f"完成绘制 {len(self.text_elements)} 个文本元素。")