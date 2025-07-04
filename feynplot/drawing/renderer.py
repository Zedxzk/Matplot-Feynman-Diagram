# /home/zed/pyfeynmandiagram/feynplot/drawing/renderer.py
# from cout import cout
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, List, Any, Tuple # 保持 Tuple 导入，因为它是标准类型提示

from regex import F
from feynplot.shared.common_functions import str2latex
import os



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

class FeynmanDiagramCanvas:
    _render_call_count = 0

    def __init__(self, fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None):
        if fig is None or ax is None:
            self.fig, self.ax = plt.subplots()
        else:
            self.fig = fig
            self.ax = ax
        
        FeynmanDiagramCanvas._render_call_count = 0
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_axis_off()
        self.fig.tight_layout()
        # self.grid_on = True

        # --- 新增：用于存储渲染参数的实例属性 ---
        # 初始为 None，表示未设置特定视图
        self._current_target_xlim: Optional[Tuple[float, float]] = None
        self._current_target_ylim: Optional[Tuple[float, float]] = None
        self._current_auto_scale: bool = False # 默认不自动缩放

    def get_axes_limits(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return self.ax.get_xlim(), self.ax.get_ylim()

    def set_axes_limits(self, xlim: Tuple[float, float], ylim: Tuple[float, float]):
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        # --- 新增：当通过 set_axes_limits 设置时，更新内部存储的参数 ---
        self._current_target_xlim = xlim
        self._current_target_ylim = ylim
        self._current_auto_scale = False # 明确设置后，auto_scale 应为 False
        self.fig.canvas.draw_idle()

    def reset_view(self):
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        # --- 新增：重置视图后，更新内部存储的参数 ---
        self._current_target_xlim = (-10, 10)
        self._current_target_ylim = (-10, 10)
        self._current_auto_scale = False
        self.fig.canvas.draw_idle()

    def _update_render_parameters(self, **kwargs: Any):
        """
        专门定义一个update_parameters的函数，用于读取render的**kwargs，然后更新到实例本身，
        然后所有函数只访问本身的属性。
        """
        # 从 kwargs 中读取 target_xlim 和 target_ylim，如果未提供则保留当前值
        self._current_target_xlim = kwargs.get('target_xlim', self._current_target_xlim)
        self._current_target_ylim = kwargs.get('target_ylim', self._current_target_ylim)
        
        # 从 kwargs 中读取 auto_scale，如果未提供则保留当前值
        self._current_auto_scale = kwargs.get('auto_scale', self._current_auto_scale)

        # 特殊处理：如果这是第一次渲染，且没有明确的 target_xlim/ylim，也没有明确 auto_scale=False
        # 那么默认进行一次自动缩放，以确保初始视图合理
        if FeynmanDiagramCanvas._render_call_count == 0 and \
           self._current_target_xlim is None and \
           not self._current_auto_scale: # 确保不是明确设置为False
            self._current_auto_scale = True


    def render(self, 
               vertices: List['Vertex'], 
               lines: List['Line'],
               **kwargs: Any): 
        
        FeynmanDiagramCanvas._render_call_count += 1
        
        # --- 调用新定义的 _update_render_parameters 来处理 kwargs ---
        self._update_render_parameters(**kwargs)

        self.ax.clear() 

        self.ax.set_aspect('equal', adjustable='box')

        # --- 根据实例属性来应用轴限制或触发自动缩放 ---
        if self._current_target_xlim is not None and self._current_target_ylim is not None:
            # 如果存在明确的目标限制，则应用这些限制
            self.ax.set_xlim(self._current_target_xlim)
            self.ax.set_ylim(self._current_target_ylim)
        elif self._current_auto_scale:
            # 如果明确要求自动缩放，则执行
            self.ax.autoscale_view()
            # 自动缩放后，更新实例属性以反映实际的视图，以便后续保持
            self._current_target_xlim = self.ax.get_xlim()
            self._current_target_ylim = self.ax.get_ylim()
        else:
            # 既没有明确限制，也没有要求自动缩放，则保持当前视图。
            # 依赖 CanvasController 传递正确的视图。
            # 这是你原代码中没有显式设置视图的“else”分支的意图。
            pass 

        # 绘制所有线
        for line in lines:
            self._draw_line(line)

        # 绘制所有顶点
        for vertex in vertices:
            self._draw_vertex(vertex)

        self.fig.tight_layout()
        self.ax.grid(True) # 保持网格线开启
        self.fig.canvas.draw_idle() 
        self.fig.canvas.flush_events() 

    def _draw_line(self, line: Line):
        line_plot_options = line.get_plot_properties()
        label_text_options = line.get_label_properties()
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
            # if line.label: # 保持原有的注释状态
            #     label_in_latex = str2latex(line.label)
            #     cout(f"Label in Latex: {label_in_latex}")
            #     input()
            #     label_x = (x1 + x2) / 2 + line.label_offset[0]
            #     label_y = (y1 + y2) / 2 + line.label_offset[1]
            #     self.ax.text(label_x, label_y, label_in_latex, **label_text_options,
            #                  zorder=line_plot_options.get('zorder', 1) + 1)
            # else: # 保持原有的注释状态
            #     input()
            #     cout(f"No label for line: {line}")
            # 通用直线的箭头绘制也需要在这里处理，可以考虑提取成辅助函数
            # ... (如果需要，添加通用直线的箭头绘制逻辑)

    def _draw_vertex(self, vertex: Vertex):
        # 绘制顶点本身 (由 plot_functions 处理高亮)
        if vertex.is_structured:
            draw_structured_vertex(self.ax, vertex)
        else:
            draw_point_vertex(self.ax, vertex)

        # # 绘制顶点标签 (独立于高亮，除非你希望高亮也影响标签样式)
        # if vertex.label: # 保持原有的注释状态
        #     label_x = vertex.x + vertex.label_offset[0]
        #     label_y = vertex.y + vertex.label_offset[1]
        #     label_text_options = vertex.get_label_properties()
        #     # 标签的 zorder 应该比顶点更高
        #     vertex_zorder = vertex.get_scatter_properties().get('zorder', 2)
        #     label_in_latex = str2latex(vertex.label)
        #     # cout(label_in_latex)
        #     cout(f"Currently drawing:{vertex.label}, {label_x}, {label_y}, {label_in_latex}")
        #     # self.ax.text(label_x, label_y, label_in_latex,
        #     #             **label_text_options, zorder=vertex_zorder + 1)
        #     # self.ax.text(label_x, label_y, label_in_latex, # 再次确保这行是注释掉的
        #     #             **label_text_options, zorder=vertex_zorder + 1) 

    def savefig(self, filename, **kwargs):
        self.fig.savefig(filename, **kwargs)

    def show(self):
        plt.show()