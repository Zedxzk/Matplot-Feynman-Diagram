# /home/zed/pyfeynmandiagram/feynplot/drawing/renderer.py
# from cout import cout
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, List, Any, Tuple 
from feynplot.drawing.fontSettings import *
from feynplot.shared.common_functions import str2latex
from feynplot.core.line_support import update_line_plot_points
from feynplot.core.extra_text_element import TextElement
from matplotlib.text import Text # 导入正确的类型

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
    get_diagram_view_limits 
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
               auto_scale: bool = False, # 【修改】从参数中读取 auto_scale 状态，默认不自动缩放
               **kwargs: Any): 
        
        # 将计数器加 1
        FeynmanDiagramCanvas._render_call_count += 1
        
        # 调用 _update_render_parameters 来处理 kwargs
        self._update_render_parameters(**kwargs)

        self.ax.clear() 
        self.ax.set_aspect('equal', adjustable='box')


        drawn_texts = []
        for text in texts:
            drawn_text = self.ax.text(**text.to_matplotlib_kwargs())
            drawn_texts.append(drawn_text)

        # # self.fig.canvas.draw()  # 确保 renderer 可用
        # renderer = self.fig.canvas.get_renderer()

        # for drawn_text in drawn_texts:
        #     bbox_pixel = drawn_text.get_window_extent(renderer=renderer)
        #     bbox_data = bbox_pixel.transformed(self.ax.transData.inverted())
        #     print(f"bbox range in data coords: x0={bbox_data.x0}, x1={bbox_data.x1}, y0={bbox_data.y0}, y1={bbox_data.y1}")



        # 绘制所有线
        for line in lines:
            self._draw_line(line)

        # 绘制所有顶点
        for vertex in vertices:
            self._draw_vertex(vertex)

        self.fig.tight_layout()
        if self.grid_on:
            self.ax.grid(True, zorder=0)
        else:
            self.ax.axis('off')

        for drawn_text in drawn_texts:
            bbox_pixel = drawn_text.get_window_extent()
            bbox_data = bbox_pixel.transformed(self.ax.transData.inverted())
            print(f"bbox range in data coords: x0={bbox_data.x0}, x1={bbox_data.x1}, y0={bbox_data.y0}, y1={bbox_data.y1}")


        # --- 根据参数和实例属性来应用轴限制或触发自动缩放 ---
        # 如果 auto_scale 为 True，则优先进行自动缩放
        if auto_scale:
            new_xlim, new_ylim = self._get_reset_view(vertices, lines, drawn_texts) 
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            # 更新内部存储的限制，以便后续渲染（当 auto_scale 为 False 时）保持此视图
            self._current_target_xlim = self.ax.get_xlim()
            self._current_target_ylim = self.ax.get_ylim()
        # 否则，如果存在明确设置的 target_xlim/ylim，则使用它们
        elif self._current_target_xlim is not None and self._current_target_ylim is not None:
            self.ax.set_xlim(self._current_target_xlim)
            self.ax.set_ylim(self._current_target_ylim)
        # 如果既没有请求自动缩放，也没有明确设置限制，且是第一次渲染，则默认自动缩放一次
        elif FeynmanDiagramCanvas._render_call_count == 1: 
            new_xlim, new_ylim = self._get_reset_view(vertices, lines) 
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            # 更新内部存储的限制
            self._current_target_xlim = self.ax.get_xlim()
            self._current_target_ylim = self.ax.get_ylim()
        # 如果是后续渲染，且没有请求自动缩放，也没有明确设置限制，则保持当前视图
        # 此时 self._current_target_xlim 和 self._current_target_ylim 会是上一次的限制
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()


    def _draw_line(self, line: Line):
        line_plot_options = line.get_plot_properties()
        label_text_options = line.get_label_properties()
        # update_line_plot_points(line)
        # self.ax.plot(line.get_line_plot_points(), line_plot_options, label_text_options)
        if isinstance(line, GluonLine):
            draw_gluon_line(self.ax, line, line_plot_options, label_text_options)
        elif isinstance(line, PhotonLine):
            draw_photon_wave(self.ax, line, line_plot_options, label_text_options)
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            draw_WZ_zigzag_line(self.ax, line, line_plot_options, label_text_options)
        elif isinstance(line, (FermionLine, AntiFermionLine)):
            draw_fermion_line(self.ax, line, line_plot_options, label_text_options)
        else: # 通用直线 (如果你的 Line 类可以直接绘制直线)
            (x1, y1), (x2, y2) = line.get_coords()
            self.ax.plot([x1, x2], [y1, y2], **line_plot_options)

    def _draw_vertex(self, vertex: Vertex):
        if vertex.is_structured:
            draw_structured_vertex(self.ax, vertex)
        else:
            draw_point_vertex(self.ax, vertex)

    def savefig(self, filename, **kwargs):
        print(f"Saving diagram to {filename}, kwargs: {kwargs}")
        # return
        self.fig.savefig(filename, **kwargs)
        self.fig.canvas.draw() 


    def show(self):
        plt.show()

    def switch_grid_state(self):
        self.grid_on = not self.grid_on

