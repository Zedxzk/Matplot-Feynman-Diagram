# /home/zed/pyfeynmandiagram/feynplot/drawing/renderer.py
# from cout import cout
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, List, Any, Tuple 
from feynplot.drawing.fontSettings import *
# from feynplot.shared.common_functions import str2latex
# from feynplot.core.line_support import update_line_plot_points
from feynplot.core.extra_text_element import TextElement
from matplotlib.text import Text # 导入正确的类型
from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection
from feynplot.default_settings.default_settings import renderer_default_settings
import numpy as np
from matplotlib.transforms import Bbox

scale_factor = renderer_default_settings['DEFAULT_SCALE_FACTOR']

# 导入你的核心模型类
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    Line, LineStyle, FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine
)

# 导入你的绘图函数
# 导入你的绘图函数，现在包括 get_diagram_view_limits
from feynplot.drawing.plot_functions import (
    draw_structured_vertex, draw_point_vertex,
    draw_gluon_line, draw_photon_wave, draw_WZ_zigzag_line, draw_fermion_line,
    get_diagram_view_limits , draw_text_element
)
class FeynmanDiagramCanvas:
    _render_call_count = 0 # Class-level counter for render calls

    def __init__(self, fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None):
        super().__init__()
        if fig is None or ax is None:
            self.fig, self.ax = plt.subplots()
        else:
            self.fig = fig
            self.ax = ax
            self.grid_on = True
        self._drawn_texts: List[Text] = []  # 用于存储绘制的文本对象
        self._drawn_lines: List[Line2D] = []  # 用于存储绘制的线对象
        self._drawn_vertices: List[PathCollection] = []  # 用于存储绘制的顶点对象
        
        # 重置实例计数器（虽然是类变量，但对于测试场景下的多个实例很有用）
        FeynmanDiagramCanvas._render_call_count = 0 
        
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_axis_off()
        self.fig.tight_layout()

        # 用于存储渲染参数的实例属性
        self._current_target_xlim: Optional[Tuple[float, float]] = None
        self._current_target_ylim: Optional[Tuple[float, float]] = None

    def get_axes_limits(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return self.ax.get_xlim(), self.ax.get_ylim()

    def set_axes_limits(self, xlim: Tuple[float, float], ylim: Tuple[float, float]):
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        # 当通过 set_axes_limits 设置时，更新内部存储的参数
        self._current_target_xlim = xlim
        self._current_target_ylim = ylim
        self.fig.canvas.draw_idle()

    def _get_reset_view(
        self,
        vertices: List[Vertex],
        lines: List[Line],
        drawn_texts: Optional[List[Text]] = None
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return get_diagram_view_limits(self.ax, vertices, lines, drawn_texts)

    def _update_render_parameters(self, **kwargs: Any):
        if 'target_xlim' in kwargs:
            self._current_target_xlim = kwargs['target_xlim']
        if 'target_ylim' in kwargs:
            self._current_target_ylim = kwargs['target_ylim']

    def render(self, 
            vertices: List[Vertex], 
            lines: List[Line],
            texts: Optional[List[TextElement]] = None,
            auto_scale: bool = False,
            zoom_times: int = 0,
            use_relative_unit: bool = True,
            **kwargs: Any):
        # 将计数器加 1
        FeynmanDiagramCanvas._render_call_count += 1
        
        # 调用 _update_render_parameters 来处理 kwargs
        self._update_render_parameters(**kwargs)
        self.ax.clear() 
        self.ax.set_aspect('equal', adjustable='box')

        # -------------------
        # 第 1 步：根据 auto_scale 决定是否重新计算视图
        # -------------------
        if auto_scale:
            new_xlim, new_ylim = self._calculate_content_bounds(vertices, lines, texts, zoom_times=zoom_times, use_relative_unit=use_relative_unit)
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self._current_target_xlim = new_xlim
            self._current_target_ylim = new_ylim
        else:
            # 否则，使用之前存储的视图限制
            if self._current_target_xlim and self._current_target_ylim:
                self.ax.set_xlim(self._current_target_xlim)
                self.ax.set_ylim(self._current_target_ylim)
            else:
                # 如果是第一次渲染，且 auto_scale 为 False，则仍然需要计算一次边界
                new_xlim, new_ylim = self._calculate_content_bounds(vertices, lines, texts, zoom_times=zoom_times, use_relative_unit=use_relative_unit)
                self.ax.set_xlim(new_xlim)
                self.ax.set_ylim(new_ylim)
                self._current_target_xlim = new_xlim
                self._current_target_ylim = new_ylim

        # 获取当前的视图限制，用于判断标签可见性
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        # -------------------
        # 第 2 步：正式绘制所有对象，并根据视图限制决定标签的可见性
        # -------------------
        
        # 绘制线，不进行可见性检查，因为线可能部分可见
        for line in lines:
            drawn_line, drawn_text = self._draw_line(line, zoom_times=zoom_times, use_relative_unit=use_relative_unit)
            # 这里你需要根据 draw_line 的返回类型进行处理，如果你修改了它
            # 你的 _draw_line 函数现在返回 (drawn_line, drawn_text)，所以我们直接使用
            if drawn_line:
                self._drawn_lines.append(drawn_line)
            if drawn_text:
                # 对于线上的标签，检查其中心点是否在视图内
                bbox = drawn_text.get_window_extent().transformed(self.ax.transData.inverted())
                center_x = (bbox.x0 + bbox.x1) / 2
                center_y = (bbox.y0 + bbox.y1) / 2
                if not (current_xlim[0] <= center_x <= current_xlim[1] and current_ylim[0] <= center_y <= current_ylim[1]):
                    drawn_text.set_visible(False) # 如果不在范围内，隐藏标签
                self._drawn_texts.append(drawn_text)


        # 绘制顶点
        for vertex in vertices:
            drawn_vertex, drawn_text = self._draw_vertex(vertex, zoom_times=zoom_times, use_relative_unit=use_relative_unit)
            if drawn_vertex:
                self._drawn_vertices.append(drawn_vertex)
            if drawn_text:
                # 对于顶点的标签，检查其中心点是否在视图内
                bbox = drawn_text.get_window_extent().transformed(self.ax.transData.inverted())
                center_x = (bbox.x0 + bbox.x1) / 2
                center_y = (bbox.y0 + bbox.y1) / 2
                if not (current_xlim[0] <= center_x <= current_xlim[1] and current_ylim[0] <= center_y <= current_ylim[1]):
                    drawn_text.set_visible(False) # 如果不在范围内，隐藏标签
                self._drawn_texts.append(drawn_text)
                
        # 如果有额外的文本，也进行绘制
        if texts:
            for text in texts:
                self._draw_text(text, zoom_times=zoom_times, use_relative_unit=use_relative_unit, **kwargs)

        # 保持网格等其他设置
        if self.grid_on:
            self.ax.grid(True, zorder=0)
            self.ax.axis('on')
        else:
            self.ax.axis('off')

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

    def _draw_line(self, line: Line, zoom_times : int = 0, use_relative_unit : bool = True, **kwargs):
        line_plot_options = line.get_plot_properties()
        label_text_options = line.get_label_properties()
        drawn_line, drawn_texts = None, None
        if 'pre_render' in kwargs and kwargs['pre_render']:
            line_plot_options['alpha'] = 0  # 设置 alpha 为 0 以隐藏线条
            label_text_options['alpha'] = 0
            kwargs.pop('pre_render', None)  # 移除 pre_render 参数
        if isinstance(line, GluonLine):
            drawn_line, drawn_texts = draw_gluon_line(self.ax, line, line_plot_options, label_text_options, zoom_times, use_relative_unit=use_relative_unit, **kwargs)
        elif isinstance(line, PhotonLine):
            drawn_line, drawn_texts = draw_photon_wave(self.ax, line, line_plot_options, label_text_options, zoom_times, use_relative_unit=use_relative_unit, **kwargs)
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            drawn_line, drawn_texts = draw_WZ_zigzag_line(self.ax, line, line_plot_options, label_text_options, zoom_times, use_relative_unit=use_relative_unit, **kwargs)
        elif isinstance(line, (FermionLine, AntiFermionLine)):
            drawn_line, drawn_texts = draw_fermion_line(self.ax, line, line_plot_options, label_text_options, zoom_times, use_relative_unit=use_relative_unit, **kwargs)
        else: # 通用直线 (如果你的 Line 类可以直接绘制直线)
            (x1, y1), (x2, y2) = line.get_coords()
            self.ax.plot([x1, x2], [y1, y2], **line_plot_options)
        # print(f"渲染线条: {line}, 绘制的线对象: {drawn_line}, 绘制的文本对象: {drawn_texts}")
        return drawn_line, drawn_texts 

    def _draw_vertex(self, vertex: Vertex, zoom_times : int = 0, use_relative_unit: bool = True,  **kwargs):

        if vertex.is_structured:
            drawn_vetex, drawn_text = draw_structured_vertex(self.ax, vertex, zoom_times=zoom_times, use_relative_unit=use_relative_unit, **kwargs)
        else:
            drawn_vetex, drawn_text = draw_point_vertex(self.ax, vertex, zoom_times=zoom_times, use_relative_unit=use_relative_unit, **kwargs)
    
        return drawn_vetex, drawn_text

    def _draw_text(self, text: TextElement, zoom_times: int = 0, use_relative_unit: bool = True, **kwargs) -> Text:
        """
        绘制额外的文本元素。
        """
        drwan_text = draw_text_element(self.ax, text, zoom_times=zoom_times, use_relative_unit=use_relative_unit, **kwargs)
        return drwan_text


    def savefig(self, filename, **kwargs):
        print(f"Saving diagram to {filename}, kwargs: {kwargs}")
        # return
        self.fig.savefig(filename, **kwargs)
        self.fig.canvas.draw() 


    def show(self):
        plt.show()

    def switch_grid_state(self):
        self.grid_on = not self.grid_on



    def _calculate_content_bounds(self, vertices, lines, texts, zoom_times: int = 0, use_relative_unit : bool = True):
        """
        预绘制部分对象并估算其他对象，以计算它们的总边界框。
        """
        # 临时清除，但保留当前视图设置
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()
        self.ax.clear()
        
        temp_drawn_objects = {}
        all_bboxes = []
        renderer = self.fig.canvas.get_renderer()

        # 1. 绘制线条和文本（不实际显示），并将它们的边界框加入列表
        for line in lines:
            drawn_line, drawn_text = self._draw_line(line, zoom_times, pre_render=True, use_relative_unit=use_relative_unit)
            if drawn_line:
                if 'line' not in temp_drawn_objects:
                    temp_drawn_objects['line'] = []
                temp_drawn_objects['line'].append(drawn_line)

            if drawn_text:
                if 'text' not in temp_drawn_objects:
                    temp_drawn_objects['text'] = []
                temp_drawn_objects['text'].append(drawn_text)

        # 绘制额外文本
        if texts:
            for text in texts:
                kwargs = text.to_matplotlib_kwargs()
                # 将 transform 参数从 transAxes 改为 transData
                drawn_text = self._draw_text(text, zoom_times=zoom_times, use_relative_unit=use_relative_unit, **kwargs)
                print(f"绘制额外文本: {drawn_text}")
                if 'text' not in temp_drawn_objects:
                    temp_drawn_objects['text'] = []
                temp_drawn_objects['text'].append(drawn_text)

        # 刷新画布以确保临时对象已渲染
        self.fig.canvas.draw()

        # 从绘制的对象中获取边界框
        for key, value in temp_drawn_objects.items():
            for obj in value:
                if obj and hasattr(obj, 'get_window_extent'):
                    try:
                        bbox = obj.get_window_extent(renderer=renderer)
                        if not any(np.isnan([bbox.x0, bbox.x1, bbox.y0, bbox.y1])) and \
                            not any(np.isinf([bbox.x0, bbox.x1, bbox.y0, bbox.y1])):
                            all_bboxes.append(bbox)
                        else:
                            print(f"bbox {bbox} is invalid, skipping.")
                    except Exception as e:
                        print(f"警告：无法获取对象 {obj} 的边界框。错误: {e}")
                        pass
                    print(f"{key} 对象的边界框: {bbox.transformed(self.ax.transData.inverted())}")
                else:
                    print(f"警告：对象 {obj} 没有有效的边界框方法，跳过。")
        # 2. 【核心修改】估算顶点的边界框，不再进行绘制
        for vertex in vertices:
            # 3. 估算半径
            # 假设 vertex.size 是以数据单位表示的，如果不是，可能需要调整
            radius = vertex.size * 0.002 
            
            # 4. 创建以 (vertex.x, vertex.y) 为中心的方形边界框（数据坐标）
            vx, vy = vertex.x, vertex.y
            data_bbox = Bbox.from_extents(vx - radius, vy - radius, vx + radius, vy + radius)
            
            # 5. 将数据坐标的bbox转换为像素坐标的bbox，以便与其他bbox合并
            pixel_bbox = data_bbox.transformed(self.ax.transData)
            all_bboxes.append(pixel_bbox)

        if not all_bboxes:
            # 如果没有有效的边界框，返回一个默认的视图
            print("警告：没有有效的绘图对象边界，使用默认视图。")
            self.ax.set_xlim(current_xlim)
            self.ax.set_ylim(current_ylim)
            # 清理临时绘制的对象
            for obj in temp_drawn_objects:
                if obj:
                    obj.remove()
            return (-5, 5), (-5, 5)
        
        for bbox in all_bboxes:
            transformed_bbox = bbox.transformed(self.ax.transData.inverted())
            print(f"Transformed bbox: {transformed_bbox}")


        # 合并所有边界框（现在包括了线条、文本和估算的顶点）
        merged_bbox = Bbox.union(all_bboxes)

        # 将合并后的像素边界框转换回数据坐标系
        merged_bbox_data = merged_bbox.transformed(self.ax.transData.inverted())
        
        # 增加边界以提供一些空白
        width = merged_bbox_data.x1 - merged_bbox_data.x0
        height = merged_bbox_data.y1 - merged_bbox_data.y0
        
        # 防止宽度或高度为0时，padding也为0的情况
        if width == 0: width = 1
        if height == 0: height = 1
            
        x_padding = width * 0.04 
        y_padding = height * 0.04

        new_xlim = (merged_bbox_data.x0 - x_padding, merged_bbox_data.x1 + x_padding)
        new_ylim = (merged_bbox_data.y0 - y_padding, merged_bbox_data.y1 + y_padding)
        
        # 清理临时绘制的对象
        for key, temp_drawn_objects in temp_drawn_objects.items():
            # print(f"清理临时绘制的对象: {key}, 对象数量: {len(temp_drawn_objects)}")
            if isinstance(temp_drawn_objects, list):
                for obj in temp_drawn_objects:
                    if obj:
                        obj.remove()
        # for obj in temp_drawn_objects:
        #     if obj:
        #         obj.remove()
                
        return new_xlim, new_ylim
