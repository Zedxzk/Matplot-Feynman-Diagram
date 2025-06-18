# feynplot_GUI/feynplot_gui/mouse_event_handler.py

import numpy as np
from PySide6.QtWidgets import QMenu 
from PySide6.QtCore import Qt, QPoint, QPointF 

# 从核心模块导入 Vertex 和 Line 基类，以便进行 isinstance 检查
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line 

class MouseEventHandler:
    def __init__(self, controller):
        self.ctrl = controller # 存储控制器实例

        self._dragged_vertex = None
        self._panning = False
        self._last_mouse_pos = None # 用于平移时记录上次鼠标的数据坐标

    def connect_events(self):
        """连接所有鼠标事件到画布。"""
        # 使用 Matplotlib 的事件系统连接事件
        self.ctrl.canvas.canvas.mpl_connect('button_press_event', self._mouse_press_event)
        self.ctrl.canvas.canvas.mpl_connect('button_release_event', self._mouse_release_event)
        self.ctrl.canvas.canvas.mpl_connect('motion_notify_event', self._mouse_move_event)
        self.ctrl.canvas.canvas.mpl_connect('scroll_event', self._scroll_event) # 连接滚轮事件

    def _mouse_press_event(self, event):
        """处理鼠标按下事件，包括拖拽和右键点击识别元素。"""
        # 确保点击发生在 Matplotlib 坐标轴内
        if event.inaxes == self.ctrl.canvas.ax: # <<< 修正：改为 .ax
            x_data, y_data = event.xdata, event.ydata

            if event.button == 1:  # 左键点击
                # 尝试选择一个顶点进行拖拽
                clicked_vertex = None
                for vertex in self.ctrl.diagram_model.vertices:
                    distance = np.sqrt((x_data - vertex.x)**2 + (y_data - vertex.y)**2)
                    if distance < 0.5: # 假设点击半径为0.5（数据坐标单位）
                        clicked_vertex = vertex
                        break

                if clicked_vertex: # 如果点击到顶点
                    self._dragged_vertex = clicked_vertex
                    # 激活顶点高亮
                    self.ctrl.highlighter.select_item(self._dragged_vertex)
                    # 记录鼠标按下的数据坐标，用于拖拽的相对位移
                    self._last_mouse_pos = (x_data, y_data) 
                else: # 如果没有点击到顶点，则开始平移
                    self._panning = True
                    self._last_mouse_pos = (x_data, y_data) # 记录平移的起始数据坐标

            elif event.button == 3:  # 右键点击
                # PySide6 的 event.guiEvent.pos() 返回 QPoint，用于菜单显示位置
                self._handle_right_click(x_data, y_data, event.guiEvent.pos())
        # else:
            # print("鼠标点击不在坐标轴内。") # 调试信息

    def _mouse_move_event(self, event):
        """处理鼠标移动事件，用于拖拽和平移。"""
        if event.inaxes == self.ctrl.canvas.ax: # <<< 修正：改为 .ax
            x_data, y_data = event.xdata, event.ydata

            if self._dragged_vertex and self._last_mouse_pos: # 拖拽顶点
                # 计算位移
                dx = x_data - self._last_mouse_pos[0]
                dy = y_data - self._last_mouse_pos[1]

                self._dragged_vertex.x += dx
                self._dragged_vertex.y += dy
                
                # 更新 _last_mouse_pos 为当前鼠标位置，以便下次移动时计算正确位移
                self._last_mouse_pos = (x_data, y_data) 
                
                self.ctrl.canvas.update_canvas() # 实时更新画布
            elif self._panning and self._last_mouse_pos: # 平移
                # 计算鼠标在数据坐标系中的位移
                dx_data = x_data - self._last_mouse_pos[0]
                dy_data = y_data - self._last_mouse_pos[1]
                
                # 获取当前的 x 和 y 限制
                xlim = self.ctrl.canvas.ax.get_xlim() # <<< 修正：改为 .ax
                ylim = self.ctrl.canvas.ax.get_ylim() # <<< 修正：改为 .ax

                # 更新限制以实现平移。注意是减去 dx/dy
                self.ctrl.canvas.ax.set_xlim(xlim[0] - dx_data, xlim[1] - dx_data) # <<< 修正：改为 .ax
                self.ctrl.canvas.ax.set_ylim(ylim[0] - dy_data, ylim[1] - dy_data) # <<< 修正：改为 .ax
                
                # 更新 _last_mouse_pos 为当前鼠标位置
                self._last_mouse_pos = (x_data, y_data)
                
                self.ctrl.canvas.canvas.draw_idle() # 异步重绘，避免卡顿
        # else:
            # print("鼠标移动不在坐标轴内。") # 调试信息

    def _mouse_release_event(self, event):
        """处理鼠标释放事件。"""
        # 重置平移和拖拽状态
        self._panning = False
        self._dragged_vertex = None
        self._last_mouse_pos = None # 清除上次鼠标位置

        # 确保在坐标轴内释放
        if event.inaxes == self.ctrl.canvas.ax: # <<< 修正：改为 .ax
            if event.button == 1: # 左键释放
                x_data, y_data = event.xdata, event.ydata
                clicked_item = self._get_item_at_coords(x_data, y_data)

                if clicked_item:
                    # 如果点击到元素，高亮它
                    self.ctrl.highlighter.select_item(clicked_item) 
                else: # 如果没有点击到任何元素 (空白处)
                    # 清除高亮
                    self.ctrl.highlighter.clear_selection() 
                
                # 无论是否点击到元素，都在释放后刷新画布
                self.ctrl.canvas.update_canvas()
        # else:
            # print("鼠标释放不在坐标轴内。") # 调试信息


    def _scroll_event(self, event):
        """处理滚轮事件，用于缩放。"""
        if event.inaxes == self.ctrl.canvas.ax: # <<< 修正：改为 .ax
            scale_factor = 1.1 if event.button == 'up' else 1 / 1.1 # 'up' 是放大，'down' 是缩小
            
            # 获取当前视图的中心点和范围
            cur_xlim = self.ctrl.canvas.ax.get_xlim() # <<< 修正：改为 .ax
            cur_ylim = self.ctrl.canvas.ax.get_ylim() # <<< 修正：改为 .ax
            
            xdata = event.xdata  # 鼠标在图中的 x 坐标
            ydata = event.ydata  # 鼠标在图中的 y 坐标

            # 确保鼠标在图内，否则使用图的中心作为缩放中心
            if xdata is None or ydata is None:
                xdata = (cur_xlim[0] + cur_xlim[1]) / 2
                ydata = (cur_ylim[0] + cur_ylim[1]) / 2

            # 计算新的视图范围
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            # 计算新的 xlim 和 ylim，使鼠标位置保持不变 (以鼠标为中心缩放)
            rel_x = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
            rel_y = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])

            new_xlim = [xdata - new_width * rel_x, xdata + new_width * (1 - rel_x)]
            new_ylim = [ydata - new_height * rel_y, ydata + new_height * (1 - rel_y)]

            self.ctrl.canvas.ax.set_xlim(new_xlim) # <<< 修正：改为 .ax
            self.ctrl.canvas.ax.set_ylim(new_ylim) # <<< 修正：改为 .ax
            self.ctrl.canvas.canvas.draw_idle() # 异步重绘

    def _get_item_at_coords(self, x_data, y_data):
        """
        根据给定的数据坐标，查找并返回最近的顶点或线条。
        """
        closest_item = None
        min_dist = float('inf')
        
        # 查找顶点 (从 diagram_model 获取)
        for v in self.ctrl.diagram_model.vertices:
            distance = np.sqrt((x_data - v.x)**2 + (y_data - v.y)**2)
            if distance < 0.5 and distance < min_dist: # 0.5 是顶点选择半径
                min_dist = distance
                closest_item = v
        
        # 查找线条 (从 diagram_model 获取)
        for l in self.ctrl.diagram_model.lines:
            if l.v_start and l.v_end:
                p1 = np.array([l.v_start.x, l.v_start.y])
                p2 = np.array([l.v_end.x, l.v_end.y])
                p_click = np.array([x_data, y_data])
                
                line_vec = p2 - p1
                line_len_sq = np.dot(line_vec, line_vec)
                
                if line_len_sq == 0: # 点线段 (如果起始和结束顶点重合)
                    distance_to_line_segment = np.linalg.norm(p_click - p1)
                else:
                    t = np.dot(p_click - p1, line_vec) / line_len_sq
                    t = max(0, min(1, t))
                    projected_point = p1 + t * line_vec
                    distance_to_line_segment = np.linalg.norm(p_click - projected_point)

                if distance_to_line_segment < 0.3 and distance_to_line_segment < min_dist: # 0.3 是线条选择半径
                    min_dist = distance_to_line_segment
                    closest_item = l
        return closest_item


    def _handle_right_click(self, x_data, y_data, gui_pos: QPoint):
        """
        处理右键点击事件，显示上下文菜单。
        :param x_data: 点击的X数据坐标
        :param y_data: 点击的Y数据坐标
        :param gui_pos: 在 GUI 窗口中的点击位置（PySide6.QtCore.QPoint）
        """
        clicked_item = self._get_item_at_coords(x_data, y_data)

        menu = QMenu(self.ctrl.canvas) # 在 canvas 上创建菜单
        
        if clicked_item:
            self.ctrl.highlighter.select_item(clicked_item) # 右键点击也选中该元素并高亮

            edit_action = menu.addAction(f"编辑 {type(clicked_item).__name__} 属性 ({clicked_item.id})")
            # 根据点击的类型，调用 ItemManager 中对应的编辑方法
            if isinstance(clicked_item, Vertex): # <<< 直接使用导入的 Vertex 类
                edit_action.triggered.connect(lambda: self.ctrl.item_manager.edit_vertex_properties(clicked_item))
            elif isinstance(clicked_item, Line): # <<< 直接使用导入的 Line 类（基类）
                edit_action.triggered.connect(lambda: self.ctrl.item_manager.edit_line_properties(clicked_item))
            else: # Fallback or error
                edit_action.setEnabled(False) # 禁用，如果类型不支持

            delete_action = menu.addAction(f"删除 {type(clicked_item).__name__} ({clicked_item.id})")
            delete_action.triggered.connect(lambda: self.ctrl.item_manager.delete_item(clicked_item))

        else: # 点击空白处
            self.ctrl.highlighter.clear_selection() # 点击空白处则清除选择
            new_vertex_action = menu.addAction("在此处添加新顶点")
            new_vertex_action.triggered.connect(lambda: self.ctrl.item_manager.add_new_vertex_at_coords(x_data, y_data))
            
            # 也可以添加添加线条的选项，但需要先选择两个顶点
            if len(self.ctrl.diagram_model.vertices) >= 2:
                add_line_action = menu.addAction("添加新线条 (选择起点和终点)")
                add_line_action.triggered.connect(lambda: self.ctrl.item_manager.start_add_line_process())
            
        menu.exec_(gui_pos) # 在鼠标点击的位置显示菜单