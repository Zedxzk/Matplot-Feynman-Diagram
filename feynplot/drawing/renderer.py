# /home/zed/pyfeynmandiagram/feynplot/drawing/renderer.py
# from cout import cout
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Optional, List, Any, Tuple, Dict 
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
import matplotlib.patches as mpatches
import feynplot.drawing.styles.arrow_styles
from contextlib import contextmanager

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
    draw_text_element
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
        self._extra_text_artists: Dict[str, Text] = {}  # text.id -> Text artist，用于命中检测时取真实边界
        self._vertex_label_artists: Dict[str, Text] = {}  # vertex.id -> label Text artist，用于 label 拖动命中
        self._line_label_artists: Dict[str, Text] = {}   # line.id -> label Text artist，用于 label 拖动命中
        self._current_target_xlim = None  # 用于存储当前目标 x 轴限制
        self._current_target_ylim = None  # 用于存储当前目标 y 轴限制
        self._transparent_background = None  # 是否使用透明背景

        # 重置实例计数器（虽然是类变量，但对于测试场景下的多个实例很有用）
        FeynmanDiagramCanvas._render_call_count = 0 
        
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_axis_off()
        self.fig.tight_layout()

        # 用于存储渲染参数的实例属性
        self._current_target_xlim: Optional[Tuple[float, float]] = None
        self._current_target_ylim: Optional[Tuple[float, float]] = None

    def get_axes_limits(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        if self._current_target_xlim and self._current_target_ylim:
            return self._current_target_xlim, self._current_target_ylim
        return self.ax.get_xlim(), self.ax.get_ylim()

    def set_axes_limits(self, xlim: Tuple[float, float], ylim: Tuple[float, float]):
        if xlim is None or ylim is None:
            if self._current_target_xlim and self._current_target_ylim:
                xlim = self._current_target_xlim
                ylim = self._current_target_ylim
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        # 当通过 set_axes_limits 设置时，更新内部存储的参数
        self._current_target_xlim = xlim
        self._current_target_ylim = ylim
        self.fig.canvas.draw_idle()

    # def _get_reset_view(
    #     self,
    #     vertices: List[Vertex],
    #     lines: List[Line],
    #     drawn_texts: Optional[List[Text]] = None
    # ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    #     return get_diagram_view_limits(self.ax, vertices, lines, drawn_texts)

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
            new_xlim, new_ylim = self._calculate_content_bounds(vertices, lines, texts, use_relative_unit=use_relative_unit)
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
                new_xlim, new_ylim = self._calculate_content_bounds(vertices, lines, texts,  use_relative_unit=use_relative_unit)
                self.ax.set_xlim(new_xlim)
                self.ax.set_ylim(new_ylim)
                self._current_target_xlim = new_xlim
                self._current_target_ylim = new_ylim

        # 获取当前的视图限制，用于判断标签可见性
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()
        # print(f"当前视图限制: xlim={current_xlim}, ylim={current_ylim}")
        # print(f"\n\n\n\n***************************DEBUG : 正式渲染 ***************************")
        # -------------------
        # 第 2 步：正式绘制所有对象，并根据视图限制决定标签的可见性
        # -------------------
        
        # 顶点/线条 label 的 artist 表，用于命中检测与拖动（每轮渲染前清空）
        self._vertex_label_artists.clear()
        self._line_label_artists.clear()
        # 绘制线，不进行可见性检查，因为线可能部分可见
        for line in lines:
            # print(f"\n********************DEBUG :渲染线条: {line}*********************************")
            drawn_line, drawn_text = self._draw_line(line, use_relative_unit=use_relative_unit, **kwargs)
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
                self._line_label_artists[line.id] = drawn_text

        # 绘制顶点
        for vertex in vertices:
            # print(f"\n********************DEBUG :渲染顶点: {vertex}*********************************")
            drawn_vertex, drawn_text = self._draw_vertex(vertex, use_relative_unit=use_relative_unit, **kwargs)
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
                self._vertex_label_artists[vertex.id] = drawn_text

        # 如果有额外的文本，也进行绘制，并保存 artist 以便命中检测使用真实边界
        self._extra_text_artists.clear()
        if texts:
            for text in texts:
                drawn_text = self._draw_text(text, use_relative_unit=use_relative_unit, **kwargs)
                if drawn_text is not None and getattr(text, 'id', None):
                    self._extra_text_artists[text.id] = drawn_text

        # 保持网格等其他设置
        if self.grid_on:
            self.ax.grid(True, zorder=-99)
            self.ax.axis('on')
        else:
            self.ax.axis('off')
        if self._transparent_background:
            self._plot_chessboard_background()
            # self.fig.patch.set_alpha(0.0)
            # self.ax.patch.set_alpha(0.0)
            # # 将 zorder 设置为 0 或更小，以确保背景图层在最下方
            # self.ax.set_zorder(-1)
        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

    def _draw_line(self, line: Line, use_relative_unit: bool = True, **kwargs):
        line_plot_options = line.get_plot_properties()
        # print(f"渲染线条: {line}, 绘制选项: {line_plot_options}, 额外参数: {kwargs}")
        label_text_options = line.get_label_properties()
        self.axis_limits = self.get_axes_limits()
        drawn_line, drawn_texts = None, None
        pre_render = kwargs.get('pre_render', False)
        if pre_render:
            # 如果是预渲染模式，设置 alpha 为 0 以隐藏线条
            # print(f"DEBUG : _draw_line() : pre_render mode activated")
            line_plot_options['alpha'] = 0  # 设置 alpha 为 0 以隐藏线条
            label_text_options['alpha'] = 0
            kwargs.pop('pre_render', None)  # 移除 pre_render 参数
        if isinstance(line, GluonLine):
            drawn_line, drawn_texts = draw_gluon_line(self.ax, line, line_plot_options, label_text_options, use_relative_unit=use_relative_unit, **kwargs)
        elif isinstance(line, PhotonLine):
            drawn_line, drawn_texts = draw_photon_wave(self.ax, line, line_plot_options, label_text_options, use_relative_unit=use_relative_unit, **kwargs)
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            drawn_line, drawn_texts = draw_WZ_zigzag_line(self.ax, line, line_plot_options, label_text_options, use_relative_unit=use_relative_unit, **kwargs)
        elif isinstance(line, (FermionLine, AntiFermionLine)):
            drawn_line, drawn_texts, drawn_arrow = draw_fermion_line(self.ax, line, line_plot_options, label_text_options, use_relative_unit=use_relative_unit, **kwargs)
        else: # 通用直线 (如果你的 Line 类可以直接绘制直线)
            (x1, y1), (x2, y2) = line.get_coords()
            self.ax.plot([x1, x2], [y1, y2], **line_plot_options)
        # print(f"渲染线条: {line}, 绘制的线对象: {drawn_line}, 绘制的文本对象: {drawn_texts}")
        return drawn_line, drawn_texts 

    def _draw_vertex(self, vertex: Vertex, use_relative_unit: bool = True, **kwargs):

        if vertex.is_structured:
            drawn_vertex, drawn_text = draw_structured_vertex(self.ax, vertex, use_relative_unit=use_relative_unit, **kwargs)
        else:
            drawn_vertex, drawn_text = draw_point_vertex(self.ax, vertex, use_relative_unit=use_relative_unit, **kwargs)

        return drawn_vertex, drawn_text

    def _draw_text(self, text: TextElement, use_relative_unit: bool = True, alpha=1, **kwargs) -> Text:
        """
        绘制额外的文本元素。
        """
        drawn_text = draw_text_element(self.ax, text, use_relative_unit=use_relative_unit, alpha=alpha, **kwargs)
        return drawn_text

    def get_extra_text_bboxes(self) -> Dict[str, Tuple[float, float, float, float]]:
        """
        返回当前绘制的「其余文本」在数据坐标系下的边界框，用于命中检测与真实显示范围一致。
        返回 dict: text_id -> (x0, y0, x1, y1)，需在 canvas 已绘制后调用。
        """
        result: Dict[str, Tuple[float, float, float, float]] = {}
        if not self._extra_text_artists:
            return result
        try:
            renderer = self.fig.canvas.get_renderer()
        except Exception:
            return result
        for text_id, artist in self._extra_text_artists.items():
            try:
                if not artist.get_visible():
                    continue
                bbox_display = artist.get_window_extent(renderer)
                bbox_data = bbox_display.transformed(self.ax.transData.inverted())
                result[text_id] = (bbox_data.x0, bbox_data.y0, bbox_data.x1, bbox_data.y1)
            except Exception:
                continue
        return result

    def get_label_bboxes(self) -> Dict[str, Tuple[float, float, float, float]]:
        """
        返回顶点标签、线条标签在数据坐标系下的边界框，用于命中检测与拖动。
        返回 dict: key 为 "vlabel:<vertex_id>" 或 "llabel:<line_id>"，value 为 (x0, y0, x1, y1)。
        """
        result: Dict[str, Tuple[float, float, float, float]] = {}
        try:
            renderer = self.fig.canvas.get_renderer()
        except Exception:
            return result
        for prefix, mapping in [("vlabel:", self._vertex_label_artists), ("llabel:", self._line_label_artists)]:
            for elem_id, artist in mapping.items():
                try:
                    if not artist.get_visible():
                        continue
                    bbox_display = artist.get_window_extent(renderer)
                    bbox_data = bbox_display.transformed(self.ax.transData.inverted())
                    result[prefix + elem_id] = (bbox_data.x0, bbox_data.y0, bbox_data.x1, bbox_data.y1)
                except Exception:
                    continue
        return result

    # 在你的 FeynmanDiagramCanvas 类中添加这个上下文管理器
    @contextmanager
    def _temporary_hide_artists(self, ax: plt.Axes):
        """
        一个上下文管理器，用于临时隐藏 zorder 小于等于指定值的艺术家。
        """
        original_visibilities = {}
        zorder_min = 0
        # 遍历 Axes 中的所有艺术家
        for artist in ax.get_children():
            original_visibilities[artist] = artist.get_visible()
            if artist.get_zorder() <= zorder_min:
                artist.set_visible(False)
                
        try:
            yield
        finally:
            # 恢复所有艺术家的原始可见性
            for artist, visible in original_visibilities.items():
                artist.set_visible(visible)


    def savefig(self, filename, **kwargs):
        """
        将图表保存到文件，只包含 zorder 大于指定值的元素。
        """
        print(f"Saving diagram to {filename}, kwargs: {kwargs}")

        # 从 kwargs 中提取 zorder_min 参数，如果不存在则使用默认值 0
        if self._transparent_background:
            kwargs['transparent'] = True
        with self._temporary_hide_artists(self.ax):
            # 在这里执行保存操作
            self.fig.savefig(filename, **kwargs)
        # 上下文管理器退出后，所有元素都会自动恢复
        self.fig.canvas.draw()

    def show(self):
        plt.show()

    def switch_grid_state(self):
        self.grid_on = not self.grid_on



    def _calculate_content_bounds(self, vertices, lines, texts, use_relative_unit : bool = True):
        """
        纯数据计算边界，不进行预绘制，避免 get_window_extent 返回无效 bbox。
        收集顶点、顶点标签、线条端点、线条标签（近似中点）、自环路径点、其余文本的位置。
        """
        xs, ys = [], []
        for v in vertices:
            xs.append(v.x)
            ys.append(v.y)
            lo = getattr(v, 'label_offset', np.array([0.0, 0.0]))
            xs.append(v.x + float(lo[0]))
            ys.append(v.y + float(lo[1]))
        for line in lines:
            if line.v_start and line.v_end:
                if getattr(line, 'loop', False):
                    # 自环：使用椭圆路径点纳入边界，否则仅顶点会漏掉环体
                    try:
                        from feynplot.core.circle import oval_circle
                        start_point = (line.v_start.x, line.v_start.y)
                        path = oval_circle(
                            start_point,
                            getattr(line, 'angular_direction', 90.0),
                            getattr(line, 'a', 1.0),
                            getattr(line, 'b', 1.0),
                            points=64
                        )
                        xs.extend(path[:, 0].tolist())
                        ys.extend(path[:, 1].tolist())
                        # 胶子/光子等自环可能有螺旋外扩，加入振幅
                        amp = getattr(line, 'amplitude', 0) or getattr(line, 'R', 0)
                        if amp > 0:
                            xs.extend([line.v_start.x - amp, line.v_start.x + amp])
                            ys.extend([line.v_start.y - amp, line.v_start.y + amp])
                    except Exception:
                        xs.extend([line.v_start.x, line.v_end.x])
                        ys.extend([line.v_start.y, line.v_end.y])
                else:
                    xs.extend([line.v_start.x, line.v_end.x])
                    ys.extend([line.v_start.y, line.v_end.y])
                mid_x = (line.v_start.x + line.v_end.x) / 2
                mid_y = (line.v_start.y + line.v_end.y) / 2
                off = getattr(line, 'label_offset', np.array([0.0, 0.0]))
                xs.append(mid_x + float(off[0]))
                ys.append(mid_y + float(off[1]))
        if texts:
            for t in texts:
                xs.append(t.x)
                ys.append(t.y)
        if not xs or not ys:
            return (-5, 5), (-5, 5)
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        width = max(x_max - x_min, 1)
        height = max(y_max - y_min, 1)
        pad_x = width * 0.10
        pad_y = height * 0.10
        return (x_min - pad_x, x_max + pad_x), (y_min - pad_y, y_max + pad_y)
    
    def _plot_chessboard_background(self, 
                                    size: float = 1.0, 
                                    color1: Tuple[float, float, float] = (1.0, 1.0, 1.0), 
                                    color2: Tuple[float, float, float] = (0.8, 0.8, 0.8)):
        """
        【高性能版】使用 numpy 和 imshow 绘制棋盘格背景。
        """
        # 确保 Figure 和 Axes 背景透明
        self.fig.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.0)

        # 获取当前视图的数据范围
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # 1. 计算棋盘格在 x 和 y 方向上需要覆盖的格子数量
        x_start = np.floor(xlim[0] / size)
        x_end = np.ceil(xlim[1] / size)
        y_start = np.floor(ylim[0] / size)
        y_end = np.ceil(ylim[1] / size)
        
        nx = int(x_end - x_start)
        ny = int(y_end - y_start)

        # 如果视图太小或无效，则不绘制
        if nx <= 0 or ny <= 0:
            return

        # 2. 使用 numpy 向量化操作创建棋盘格图案 (0和1交替)
        # 创建每个格子的绝对索引
        x_indices = np.arange(nx) + int(x_start)
        y_indices = np.arange(ny) + int(y_start)
        # 使用 meshgrid 和广播创建二维索引网格，并计算 (x+y)%2
        X, Y = np.meshgrid(x_indices, y_indices)
        pattern = (X + Y) % 2

        # 3. 根据图案 (pattern) 创建一个 RGB 图像数组
        # 创建一个 (ny, nx, 3) 的全零数组
        image = np.zeros((ny, nx, 3))
        
        # 使用布尔索引一次性为所有格子赋值颜色，这比循环快几个数量级
        image[pattern == 0] = color1
        image[pattern == 1] = color2

        # 4. 使用 imshow 将图像绘制在背景上
        # extent 参数定义了图像在数据坐标系中的位置和大小
        extent = (x_start * size, x_end * size, y_start * size, y_end * size)
        
        # origin='lower' 确保 (0,0) 索引在左下角，符合笛卡尔坐标系
        # interpolation='nearest' 确保格子边缘清晰，没有模糊
        self.ax.imshow(image, origin='lower', extent=extent, 
                    interpolation='nearest', zorder=-100)

        # 重新设置坐标轴范围，因为 imshow 可能会轻微改变它
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

    def change_transparent_background_state(self, state: bool = None):
        if state is not None:
            self._transparent_background = state
        else:
            self._transparent_background = not self._transparent_background