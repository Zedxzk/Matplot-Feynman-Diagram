# /home/zed/pyfeynmandiagram/feynplot/drawing/renderer.py
# from cout import cout
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, List

# 导入你的核心模型类
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    Line, LineStyle, FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine
)

# 导入你的绘图函数
from feynplot.drawing.plot_functions import (
    draw_structured_vertex, draw_point_vertex,
    draw_gluon_line, draw_photon_wave, draw_WZ_zigzag_line, draw_fermion_line,
    # 确保如果你有通用的直线绘制函数，也在这里导入
)

class MatplotlibBackend:
    def __init__(self, fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None):
        if fig is None or ax is None:
            self.fig, self.ax = plt.subplots()
        else:
            self.fig = fig
            self.ax = ax

        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_axis_off()
        self.fig.tight_layout()

    def get_axes_limits(self):
        return self.ax.get_xlim(), self.ax.get_ylim()

    def set_axes_limits(self, xlim: tuple, ylim: tuple):
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.fig.canvas.draw_idle()

    def reset_view(self):
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.fig.canvas.draw_idle()

    def render(self, vertices: List[Vertex], lines: List[Line]):
        self.ax.clear()
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_axis_off()

        # 绘制所有线
        for line in lines:
            self._draw_line(line)

        # 绘制所有顶点
        for vertex in vertices:
            self._draw_vertex(vertex)

        self.fig.tight_layout()
        self.ax.autoscale_view() # 自动调整视图以包含所有元素
        self.fig.canvas.draw_idle() # 在渲染结束后触发一次绘制

    def _draw_line(self, line: Line):
        line_plot_options = line.get_plot_properties()
        label_text_options = line.get_label_properties()
        # print(f'plot options: {line_plot_options}    ')
        # print(f"label options: {label_text_options}")
        # print(f"Plot Line: {line}")
        # input()
        # 直接将 is_selected 状态传递给绘图函数
        # 绘图函数会根据此状态自行调整样式（包括高亮）
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
            # 对于通用直线，如果需要箭头或标签，也需要在_draw_line中处理
            if line.label:
                label_x = (x1 + x2) / 2 + line.label_offset[0]
                label_y = (y1 + y2) / 2 + line.label_offset[1]
                self.ax.text(label_x, label_y, line.label, **label_text_options,
                             zorder=line_plot_options.get('zorder', 1) + 1)
            # 通用直线的箭头绘制也需要在这里处理，可以考虑提取成辅助函数
            # ... (如果需要，添加通用直线的箭头绘制逻辑)

    def _draw_vertex(self, vertex: Vertex):
        # 绘制顶点本身 (由 plot_functions 处理高亮)
        if vertex.is_structured:
            draw_structured_vertex(self.ax, vertex)
        else:
            draw_point_vertex(self.ax, vertex)

        # 绘制顶点标签 (独立于高亮，除非你希望高亮也影响标签样式)
        if vertex.label:
            label_x = vertex.x + vertex.label_offset[0]
            label_y = vertex.y + vertex.label_offset[1]
            label_text_options = vertex.get_label_properties()
            # 标签的 zorder 应该比顶点更高
            vertex_zorder = vertex.get_scatter_properties().get('zorder', 2)
            self.ax.text(label_x, label_y, vertex.label,
                         **label_text_options, zorder=vertex_zorder + 1)

    def savefig(self, filename, **kwargs):
        self.fig.savefig(filename, **kwargs)

    def show(self):
        plt.show()