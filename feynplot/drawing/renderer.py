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
from feynplot.default_settings.default_settings import renderer_default_settings

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
               zoom_times : int = 0,
               **kwargs: Any): 
        
        # 将计数器加 1
        FeynmanDiagramCanvas._render_call_count += 1
        
        # 调用 _update_render_parameters 来处理 kwargs
        self._update_render_parameters(**kwargs)

        self.ax.clear() 
        self.ax.set_aspect('equal', adjustable='box')


        drawn_texts = []
 
        # # self.fig.canvas.draw()  # 确保 renderer 可用
        # renderer = self.fig.canvas.get_renderer()

        # for drawn_text in drawn_texts:
        #     bbox_pixel = drawn_text.get_window_extent(renderer=renderer)
        #     bbox_data = bbox_pixel.transformed(self.ax.transData.inverted())
        #     print(f"bbox range in data coords: x0={bbox_data.x0}, x1={bbox_data.x1}, y0={bbox_data.y0}, y1={bbox_data.y1}")

        # 绘制所有线
        for line in lines:
            drawn_line, drawn_text = self._draw_line(line, zoom_times)
            drawn_texts.append(drawn_text)

        # 绘制所有顶点
        for vertex in vertices:
            drawn_text = self._draw_vertex(vertex, zoom_times)
            drawn_texts.append(drawn_text)

        self.fig.tight_layout()

        for text in texts:
            kwargs = text.to_matplotlib_kwargs()
            # 检查 'color' 键是否存在，然后删除它
            if 'color' in kwargs:
                del kwargs['color']
            kwargs['size'] = kwargs['size'] / (scale_factor) ** zoom_times

            # 绘制文本，并用 color='none' 覆盖
            drawn_text = self.ax.text(alpha=0, **kwargs, transform=self.ax.transAxes)
            drawn_texts.append(drawn_text)



        if self.grid_on:
            self.ax.grid(True, zorder=0)
        else:
            self.ax.axis('off')

        # for drawn_text in drawn_texts:
        #     bbox_pixel = drawn_text.get_window_extent()
        #     bbox_data = bbox_pixel.transformed(self.ax.transData.inverted())
        #     print(f"bbox range in data coords: x0={bbox_data.x0}, x1={bbox_data.x1}, y0={bbox_data.y0}, y1={bbox_data.y1}")

        self.fig.canvas.draw_idle()
        # self.fig.canvas.flush_events()


        # --- 根据参数和实例属性来应用轴限制或触发自动缩放 ---
        # 如果 auto_scale 为 True，则优先进行自动缩放
        if auto_scale or FeynmanDiagramCanvas._render_call_count <= 1:
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

            xlim = self._current_target_xlim
            ylim = self._current_target_ylim

            # for drawn_text in drawn_texts:
            #     bbox_pixel = drawn_text.get_window_extent()
            #     bbox_data = bbox_pixel.transformed(self.ax.transData.inverted())

            #     # 计算文本中心点
            #     center_x = (bbox_data.x0 + bbox_data.x1) / 2
            #     center_y = (bbox_data.y0 + bbox_data.y1) / 2

            #     # 如果中心点不在视图范围内，则移除文本
            #     if not (xlim[0] <= center_x <= xlim[1] and ylim[0] <= center_y <= ylim[1]):
            #         drawn_text.remove()

                
        else:
            print("Unexpected case")
            raise RuntimeError("Unexpected case")
        # 如果是后续渲染，且没有请求自动缩放，也没有明确设置限制，则保持当前视图
        # 此时 self._current_target_xlim 和 self._current_target_ylim 会是上一次的限制
        

        for text in texts:
            kwargs = text.to_matplotlib_kwargs()
            # 检查 'color' 键是否存在，然后删除它
            kwargs['size'] = kwargs['size'] / (scale_factor) ** zoom_times
            # 绘制文本，并用 color='none' 覆盖
            drawn_text = self.ax.text(**kwargs, transform=self.ax.transAxes, )
            drawn_texts.append(drawn_text)
        self.fig.canvas.draw_idle()
        # self.ax.axhline(0.1)
        # self.ax.axhline(-0.1)



    def _draw_line(self, line: Line, zoom_times : int = 0, **kwargs):
        line_plot_options = line.get_plot_properties()
        label_text_options = line.get_label_properties()
        drawn_line, drawn_texts = None, None
        # update_line_plot_points(line)
        # self.ax.plot(line.get_line_plot_points(), line_plot_options, label_text_options)
        if isinstance(line, GluonLine):
            drawn_line, drawn_texts = draw_gluon_line(self.ax, line, line_plot_options, label_text_options, zoom_times)
        elif isinstance(line, PhotonLine):
            drawn_line, drawn_texts = draw_photon_wave(self.ax, line, line_plot_options, label_text_options, zoom_times)
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            drawn_line, drawn_texts = draw_WZ_zigzag_line(self.ax, line, line_plot_options, label_text_options, zoom_times)
        elif isinstance(line, (FermionLine, AntiFermionLine)):
            drawn_line, drawn_texts = draw_fermion_line(self.ax, line, line_plot_options, label_text_options, zoom_times)
        else: # 通用直线 (如果你的 Line 类可以直接绘制直线)
            (x1, y1), (x2, y2) = line.get_coords()
            self.ax.plot([x1, x2], [y1, y2], **line_plot_options)

        return drawn_line, drawn_texts 

    def _draw_vertex(self, vertex: Vertex, zoom_times : int = 0,  **kwargs):
        if vertex.is_structured:
            drawn_text = draw_structured_vertex(self.ax, vertex, zoom_times=zoom_times)
        else:
            drawn_text = draw_point_vertex(self.ax, vertex, zoom_times=zoom_times)
        return drawn_text

    def savefig(self, filename, **kwargs):
        print(f"Saving diagram to {filename}, kwargs: {kwargs}")
        # return
        self.fig.savefig(filename, **kwargs)
        self.fig.canvas.draw() 


    def show(self):
        plt.show()

    def switch_grid_state(self):
        self.grid_on = not self.grid_on

