# feynplot_GUI/feynplot_gui/selection_highlighter.py

# --- 直接导入 Vertex 和 Line 类 ---
from feynplot.core.vertex import Vertex  # 确保这个导入路径是正确的
from feynplot.core.line import Line      # 确保这个导入路径是正确的

class SelectionHighlighter: # 假设你的类名就是 SelectionHighlighter
    def __init__(self, controller):
        self.ctrl = controller
        self._selected_item_data = None  # 存储当前选中的模型数据 (Vertex 或 Line 实例)
        self._original_properties = {}   # 存储原始属性以便后续恢复

    def set_selected_item(self, item_data):
        """设置要选中的项并触发刷新。"""
        if self._selected_item_data is item_data:
            return # 选中项没有改变

        self.clear_highlight() # 在设置新选择之前清除之前的高亮
        self._selected_item_data = item_data
        self.highlight_selected_item()
        self.ctrl.canvas.update_canvas() # 确保在选择更改后画布重绘


    def clear_highlight(self):
        """
        清除之前高亮元素的属性，并重绘画布。
        不清除 _selected_item_data，只清除视觉效果。
        """
        if self._selected_item_data and self._selected_item_data in self._original_properties:
            original_props = self._original_properties.pop(self._selected_item_data)
            
            # --- 使用直接导入的 Vertex 类进行检查 ---
            if isinstance(self._selected_item_data, Vertex):
                self._selected_item_data.is_selected = False
                self._selected_item_data.color = original_props.get('color', 'blue') # 如果没找到，使用默认值
                self._selected_item_data.linewidth = original_props.get('linewidth', 1.0)
                self._selected_item_data.edgecolor = original_props.get('edgecolor', self._selected_item_data.color)
                self._selected_item_data.size = original_props.get('size', 100)
                print(f"DEBUG: 清除高亮 Vertex ID={self._selected_item_data.id}, 恢复颜色='{self._selected_item_data.color}'")
            
            # --- 使用直接导入的 Line 类进行检查 ---
            elif isinstance(self._selected_item_data, Line):
                if hasattr(self._selected_item_data, 'linePlotConfig') and isinstance(self._selected_item_data.linePlotConfig, dict):
                    self._selected_item_data.is_selected = False
                    self._selected_item_data.color = original_props.get('color', 'black')
                    self._selected_item_data.linewidth = original_props.get('linewidth', 1.0)
                    self._selected_item_data.color = 'red'
                    self._selected_item_data.linewidth = 3.0
                    print(f"DEBUG: 清除高亮 Line ID={self._selected_item_data.id}, 恢复颜色='{self._selected_item_data.linePlotConfig().get('color', 'N/A')}'")
        
        # 清除后，重绘画布以应用更改
        self.ctrl.canvas.update_canvas()


    def highlight_selected_item(self):
        """
        根据 _selected_item_data 设置模型元素的选中状态，并应用高亮属性。
        """
        # 这些调试打印暂时保留，它们不会导致错误
        if self.ctrl.diagram_model:
            l_mu = self.ctrl.diagram_model.get_line_by_id('l_mu')
            l_e2 = self.ctrl.diagram_model.get_line_by_id('l_e2')
            l_gamma = self.ctrl.diagram_model.get_line_by_id('l_gamma')
            
            print("--- DEBUG(BEFORE highlight): 当前线条颜色和配置地址 ---")
            if l_mu: print(f"l_mu: 颜色='{l_mu.linePlotConfig().get('color', 'N/A')}', 配置地址={id(l_mu.linePlotConfig)}")
            if l_e2: print(f"l_e2: 颜色='{l_e2.linePlotConfig().get('color', 'N/A')}', 配置地址={id(l_e2.linePlotConfig)}")
            if l_gamma: print(f"l_gamma: 颜色='{l_gamma.linePlotConfig().get('color', 'N/A')}', 配置地址={id(l_gamma.linePlotConfig)}")
            print("--------------------------------------------------")

        # 设置选中项的状态和高亮属性
        if self._selected_item_data:
            original_props = {}
            
            # --- 修正：使用直接导入的 Vertex 和 Line 类进行 isinstance 检查 ---
            if isinstance(self._selected_item_data, Vertex):
                original_props = {
                    'color': self._selected_item_data.color,
                    'linewidth': self._selected_item_data.linewidth,
                    'edgecolor': self._selected_item_data.edgecolor,
                    'size': self._selected_item_data.size
                }
                self._selected_item_data.is_selected = True

                self._selected_item_data.edgecolor = 'red'
                self._selected_item_data.size = 200
                print(f"DEBUG: 应用高亮到 Vertex ID={self._selected_item_data.id}, 新颜色='{self._selected_item_data.color}'")

            elif isinstance(self._selected_item_data, Line):
                if hasattr(self._selected_item_data, 'linePlotConfig') and isinstance(self._selected_item_data.linePlotConfig, dict):
                    original_props = {
                        'color': self._selected_item_data.linePlotConfig().get('color', 'black'),
                        'linewidth': self._selected_item_data.linePlotConfig().get('linewidth', 1.0)
                    }
                    self._selected_item_data.is_selected = True
                    self._selected_item_data.color = 'red'
                    self._selected_item_data.linewidth = 3.0
                    print(f"DEBUG: 应用高亮到 Line ID={self._selected_item_data.id}, 新颜色='{self._selected_item_data.linePlotConfig().get('color', 'N/A')}'")
                else:
                    print(f"警告: 选中的线条对象 {self._selected_item_data.id} 没有 linePlotConfig 字典，无法高亮其绘图属性。")
                    self._selected_item_data.is_selected = True 
            
            if original_props:
                self._original_properties[self._selected_item_data] = original_props
                print(f"高亮显示: ID={self._selected_item_data.id}, 类型={type(self._selected_item_data).__name__}")
            else:
                print(f"警告: 未能为 {self._selected_item_data.id} (类型: {type(self._selected_item_data).__name__}) 收集到有效的原始绘图属性。")

        else:
            print("没有选中项，无需高亮。")

        # 这些调试打印也暂时保留
        if self.ctrl.diagram_model:
            l_mu = self.ctrl.diagram_model.get_line_by_id('l_mu')
            l_e2 = self.ctrl.diagram_model.get_line_by_id('l_e2')
            l_gamma = self.ctrl.diagram_model.get_line_by_id('l_gamma')
            
            print("--- DEBUG(AFTER highlight): 当前线条颜色和配置地址 ---")
            if l_mu: print(f"l_mu: 颜色='{l_mu.linePlotConfig().get('color', 'N/A')}', 配置地址={id(l_mu.linePlotConfig)}")
            if l_e2: print(f"l_e2: 颜色='{l_e2.linePlotConfig().get('color', 'N/A')}', 配置地址={id(l_e2.linePlotConfig)}")
            if l_gamma: print(f"l_gamma: 颜色='{l_gamma.linePlotConfig().get('color', 'N/A')}', 配置地址={id(l_gamma.linePlotConfig)}")
            print("-------------------------------------------------")

        # self.ctrl.canvas.update_canvas() # 这行代码应该由 set_selected_item 或 Controller 中的 update_view 管理