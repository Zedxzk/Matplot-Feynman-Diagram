import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
from feynplot_gui.debug_utils import cout
from feynplot.shared.common_functions import str2latex
from feynplot.core.extra_text_element import TextElement
import matplotlib.colors as mcolors # 新增：导入颜色模块
from matplotlib.text import Text
from matplotlib.axes import Axes
from feynplot.default_settings.default_settings import renderer_default_settings
from typing import Union
from feynplot.drawing.styles.arrow_styles import FishtailArrow

scaling_factor = renderer_default_settings["DEFAULT_SCALE_FACTOR"]

# 导入你的核心模型类（如果这些函数直接依赖于 Line 和 Vertex 对象）
# 这些导入最好放在文件的顶部，以便清晰可见。
from feynplot.core.line import Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine, WPlusLine, WMinusLine, ZBosonLine
from feynplot.core.vertex import Vertex

# 导入生成路径的方法
from feynplot.core.gluon_methods import generate_gluon_helix
from feynplot.core.photon_methods import generate_photon_wave
from feynplot.core.WZ_methods import generate_WZ_zigzag
from feynplot.core.fermion_methods import generate_fermion_line
import mplhep as hep

from feynplot.drawing.fontSettings import *
from typing import List, Tuple, Optional, Any, Dict

highlight_color = 'red'

def draw_photon_wave(ax, line: PhotonLine, line_plot_options: dict, label_text_options: dict,  use_relative_unit: bool = True, **kwargs):
    # 复制字典以避免修改原始对象内部的配置
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()

    original_linewidth = current_line_plot_options.get('linewidth', 1.5)
    original_color = current_line_plot_options.get('color', 'black')
    original_zorder = current_line_plot_options.get('zorder', 1) # 线的默认 zorder 为 1

    # 如果线被选中，调整绘图属性
    if line.is_selected:
        current_line_plot_options['color'] = highlight_color # 高亮颜色
        current_line_plot_options['linewidth'] = original_linewidth * 1.5 + 3 # 增加线宽
        current_line_plot_options['zorder'] = original_zorder + 10 # 提高 Z-order

        # 标签也可能需要调整，例如颜色或 Z-order
        current_label_text_options['color'] = highlight_color
        current_label_text_options['zorder'] = original_zorder + 11

    # 获取光子波的路径点
    wave_path = generate_photon_wave(line, loop=line.loop)
    x_wave, y_wave = wave_path[:, 0], wave_path[:, 1]

    # 绘制光子波的路径，使用调整后的属性
    line.set_plot_points(x_wave, y_wave)
    drawn_line = draw_line(ax, line=line, line_plot_options=current_line_plot_options, use_relative_unit=use_relative_unit, **kwargs)
    drawn_text = draw_line_label(ax, line, label_text_options,  **kwargs) # 绘制标签
    return drawn_line, drawn_text


def draw_gluon_line(ax, line: GluonLine, line_plot_options: dict, label_text_options: dict,  use_relative_unit: bool = True, **kwargs):
    # print('Detected GluonLine') # 可以保留用于调试
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()

    original_linewidth = current_line_plot_options.get('linewidth', 1.5)
    original_color = current_line_plot_options.get('color', 'black')
    original_zorder = current_line_plot_options.get('zorder', 1)

    # 如果线被选中，调整绘图属性
    if line.is_selected:
        current_line_plot_options['color'] = highlight_color
        current_line_plot_options['linewidth'] = original_linewidth * 1.5 + 3
        current_line_plot_options['zorder'] = original_zorder + 10

        current_label_text_options['color'] = highlight_color
        current_label_text_options['zorder'] = original_zorder + 11

    # 获取胶子线的路径点
    bezire_path, helix_path = line.get_plot_path()
    x_helix, y_helix = helix_path[:, 0], helix_path[:, 1]

    # 绘制胶子线的路径
    line.set_plot_points(x_helix, y_helix)
    drawn_line = draw_line(ax, line, current_line_plot_options)

    drawn_text = draw_line_label(ax, line, label_text_options, **kwargs) # 绘制标签
    return drawn_line, drawn_text 


def draw_WZ_zigzag_line(ax, line: Line, line_plot_options: dict, label_text_options: dict,  use_relative_unit: bool = True, **kwargs):
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()

    original_linewidth = current_line_plot_options.get('linewidth', 1.5)
    original_color = current_line_plot_options.get('color', 'black')
    original_zorder = current_line_plot_options.get('zorder', 1)

    # 调用 generate_WZ_zigzag 获取所有路径
    zigzag_path, base_path = generate_WZ_zigzag(line) 

    # --- 绘制高分辨率贝塞尔曲线 (背景线) ---
    high_res_bezier_plot_options = current_line_plot_options.copy() # 基于当前线条属性复制
    high_res_bezier_plot_options['linestyle'] = ':'
    high_res_bezier_plot_options['linewidth'] = original_linewidth * 0.25 # 总是使用原始线宽的比例
    high_res_bezier_plot_options['color'] = 'lightgray' # 总是浅灰色
    high_res_bezier_plot_options['zorder'] = original_zorder # 确保在所有线的最底层

    # ax.plot(high_res_bezier_path[:, 0], high_res_bezier_path[:, 1], **high_res_bezier_plot_options)

    # 如果线被选中，调整主要锯齿线的绘图属性
    if line.is_selected:
        current_line_plot_options['color'] = highlight_color
        current_line_plot_options['linewidth'] = original_linewidth * 1.5 + 3
        current_line_plot_options['zorder'] = original_zorder + 10 # 锯齿线的高亮 Z-order

        current_label_text_options['color'] = highlight_color
        current_label_text_options['zorder'] = original_zorder + 11 # 标签的高亮 Z-order

    # --- 绘制锯齿路径 (主要线条) ---
    x_zig, y_zig = zigzag_path[:, 0], zigzag_path[:, 1]
    line.set_plot_points(x_zig, y_zig)
    drawn_line = draw_line(ax, line, current_line_plot_options)
     

    drawn_text = draw_line_label(ax, line, label_text_options, **kwargs) # 绘制标签
    return drawn_line, drawn_text


def draw_fermion_line(ax, line: FermionLine, line_plot_options: dict, label_text_options: dict, use_relative_unit: bool = True, **kwargs):
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()

    # print(f"\n\n Drawing Fermion DEBUG: current_line_plot_options: {current_line_plot_options}\n")
    # print(f"\n Drawing Fermion DEBUG: current_label_text_options: {current_label_text_options}")
    drawn_text, drawn_arrow, drawn_line = None, None, None
    original_linewidth = current_line_plot_options.get('linewidth', 1.5)
    original_color = current_line_plot_options.get('color', 'black')
    original_zorder = current_line_plot_options.get('zorder', 1)

    # 如果线被选中，调整绘图属性
    if line.is_selected:
        current_line_plot_options['color'] = highlight_color
        current_line_plot_options['linewidth'] = original_linewidth * 1.5 + 3
        current_line_plot_options['zorder'] = original_zorder + 10

        current_label_text_options['color'] = highlight_color
        current_label_text_options['zorder'] = original_zorder + 11

    # 获取费米子线路径
    fermion_path = generate_fermion_line(line)
    x, y = fermion_path[:, 0], fermion_path[:, 1]

    # 绘制费米子线本身
    line.set_plot_points(x, y)
    # print(f"DEBUG: 绘制费米子线: {line}, 绘制选项: {current_line_plot_options}")
    drawn_line = draw_line(ax, line, current_line_plot_options)
    # from pprint import pprint
    # points = line.get_line_plot_points()[:10]
    # formatted_points = [f"({x:.3f}, {y:.3f})" for (x, y) in points]
    # pprint(f"fermion_path: {formatted_points}")
    # print(f"DEBUG, 绘制费米子线: {line}, arrow={line.arrow}"    )
    # --- 绘制箭头 ---
    if line.arrow and len(x) > 1:
        arrow_filled = getattr(line, 'arrow_filled', False)
        arrow_position = getattr(line, 'arrow_position', 0.5)
        arrow_size = getattr(line, 'arrow_size', 1.0)
        arrow_line_width = getattr(line, 'arrow_line_width', None)
        arrow_reversed = getattr(line, 'arrow_reversed', False)

        if len(x) < 2:
            return

        idx_tip = int(round(arrow_position * (len(x) - 1)))

        if idx_tip == 0:
            idx_base = 1
        elif idx_tip >= len(x) - 1:
            idx_base = len(x) - 2
        else:
            idx_base = idx_tip - 1


        p_tip = (x[idx_tip], y[idx_tip])
        p_base = (x[idx_base], y[idx_base])

        if arrow_reversed:
            xy = p_base
            xytext = p_tip
        else:
            xy = p_tip
            xytext = p_base

        arrow_style_str = line.get_arrow_properties()

        arrow_lw = arrow_line_width if arrow_line_width is not None else \
                           current_line_plot_options.get('linewidth', 1.5)
        # if current_label_text_options['alpha']  == 0:
        #     # 如果标签的 alpha 为 0，则不绘制箭头
        #     arrow_style_str
        # print(f"\n\n DEBUG : arrow alpha {label_text_options.get('alpha', 1.0)}， label_text_options: {label_text_options}")
        arrow_props = dict(
            arrowstyle=arrow_style_str,
            linewidth=arrow_lw,
            color=current_line_plot_options.get('color', 'black'),
            zorder=current_line_plot_options.get('zorder', 1) + 1,
            alpha=label_text_options.get('alpha', 1.0) # 将 alpha 添加到这里
        )

        # ax.annotate(
        #     '',
        #     xy=xy,
        #     xytext=xytext,
        #     arrowprops=arrow_props,
        # )

        drawn_arrow = draw_arrow(ax, xy, xytext,
            linewidth=arrow_lw,
            arrow_props=arrow_props,
            color=current_line_plot_options.get('color', 'black'),
            zorder=current_line_plot_options.get('zorder', 1) + 1,
            alpha=label_text_options.get('alpha', 1.0), # 将 alpha 添加到这里 ,
            is_selected=line.is_selected,
            mutation_scale=line.mutation_scale,
            arrow_angle=line.arrow_angle,
            arrow_tail_angle=line.arrow_tail_angle,
            arrow_offset_ratio=line.arrow_offset_ratio
            )

    drawn_text = draw_line_label(ax, line, label_text_options, use_relative_unit=use_relative_unit, **kwargs) # 绘制标签
    return drawn_line, drawn_text, drawn_arrow


def draw_point_vertex(ax: plt.Axes, vertex: Vertex,  use_relative_unit: bool = True, **kwargs):
    # 复制字典以避免修改原始对象内部的配置
    drawn_vertex, drawn_text = None, None
    current_scatter_props = vertex.get_scatter_properties().copy()
    current_label_props = vertex.get_label_properties().copy()
    if 'pre_render' in kwargs and kwargs['pre_render']:
        # 设置 alpha 为 0 以隐藏顶点
        current_scatter_props['alpha'] = 0
        current_label_props['alpha'] = 0
        kwargs.pop('pre_render', None)

    cout(f"current_scatter_props: {current_scatter_props}")
    cout(f"current_label_props: {current_label_props}")

    # 移除冲突的参数
    if 'c' in current_scatter_props and 'color' in current_scatter_props:
        current_scatter_props.pop('c')
    # 如果有 size 参数，替换成 s
    if 'size' in current_scatter_props:
        current_scatter_props['s'] = current_scatter_props.pop('size')


    # original_size = current_scatter_props.get('s', 100)
    # original_color = current_scatter_props.get('c', 'blue')
    # original_edgecolor = current_scatter_props.get('edgecolor', original_color)
    # original_linewidth = current_scatter_props.get('linewidth', 1.0)
    # original_zorder = current_scatter_props.get('zorder', 2) # 顶点的默认 zorder 为 2

    current_scatter_props = convert_props_from_data(ax, current_scatter_props, use_relative_unit=use_relative_unit)

    # 如果顶点被选中，调整绘图属性
    if vertex.is_selected:
        current_scatter_props['s'] *= 1.5 # 放大
        current_scatter_props['c'] = highlight_color # 变色
        current_scatter_props['edgecolor'] = highlight_color
        current_scatter_props['linewidth'] += 1.0
        current_scatter_props['zorder'] += 10 # 提高 Z-order

        # 标签也可能需要调整
        current_label_props['color'] = highlight_color
        current_label_props['zorder'] = current_scatter_props.get('zorder', 2) + 10 # 提高标签的 Z-order
    # --- 绘制点状顶点 ---
    # print(f"kwargs: {kwargs}")
    if not vertex.hidden_vertex or vertex.is_selected:
        cout(current_scatter_props)
        drawn_vertex = ax.scatter(vertex.x, vertex.y, **current_scatter_props, **kwargs)

    # 绘制标签
    drawn_text = draw_vertex_label(ax, vertex, current_label_props, use_relative_unit=use_relative_unit, **kwargs)

    return drawn_vertex, drawn_text


def draw_structured_vertex(ax: plt.Axes, vertex: Vertex,  use_relative_unit: bool = True, **kwargs):
    # 复制字典以避免修改原始对象内部的配置
    current_circle_props = vertex.get_circle_properties().copy()
    current_custom_hatch_props = vertex.get_custom_hatch_properties().copy()
    current_label_props = vertex.get_label_properties().copy()

    original_linewidth = current_circle_props.get('linewidth', 1.5)
    original_edgecolor = current_circle_props.get('edgecolor', 'black')
    original_zorder = current_circle_props.get('zorder_structured', 10)

    if vertex.hidden_vertex and not vertex.is_selected:
        return

    current_circle_props = convert_props_from_data(ax, current_circle_props, use_relative_unit=use_relative_unit)

    # 如果顶点被选中，调整绘图属性
    if vertex.is_selected:
        current_circle_props['edgecolor'] = 'yellow' # 边框变色
        current_circle_props['linewidth'] = original_linewidth + 1.5 # 增加线宽
        current_circle_props['zorder'] = original_zorder + 10 # 提高 Z-order

        # 如果有自定义阴影线，也可能需要调整其颜色或线宽
        current_custom_hatch_props['hatch_line_color'] = highlight_color # 阴影线颜色
        # current_custom_hatch_props['hatch_line_width'] = current_custom_hatch_props.get('hatch_line_width', 0.5) + 0.5

        current_label_props['color'] = highlight_color
        current_label_props['zorder'] = original_zorder + 11


    # 1. 绘制圆圈主体
    # --- 新增圆圈可见性检查 ---
    circle_center_x = vertex.x
    circle_center_y = vertex.y
    circle_radius = current_circle_props.get('radius', 0.1) # 获取圆的半径
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # 简单检查：圆心在视图内，或圆的任何一部分与视图边界重叠
    # 这是一个比较粗略的检查，但对于性能优化来说通常足够
    is_circle_visible = (
        (circle_center_x + circle_radius > xlim[0] and circle_center_x - circle_radius < xlim[1]) and
        (circle_center_y + circle_radius > ylim[0] and circle_center_y - circle_radius < ylim[1])
    )

    if is_circle_visible:
        circle = Circle(
            (vertex.x, vertex.y),
            **current_circle_props
        )
        drawn_vertex = ax.add_patch(circle, **kwargs)
    else:
        # 如果圆圈不可见，则其阴影线和标签也不需要绘制
        return


    # 2. 绘制阴影线 (如果使用自定义模式)
    if vertex.use_custom_hatch and is_circle_visible: # 只有当圆圈可见时才绘制阴影线
        hatch_line_color = current_custom_hatch_props['hatch_line_color']
        hatch_line_width = current_custom_hatch_props['hatch_line_width']
        hatch_line_angle_deg = current_custom_hatch_props['hatch_line_angle_deg']
        hatch_spacing_ratio = current_custom_hatch_props['hatch_spacing_ratio']

        radius = vertex.structured_radius
        center_x = vertex.x
        center_y = vertex.y
        zorder_hatch = current_circle_props['zorder'] + 0.5 # 阴影线在圆圈之上，但仍低于标签

        angle_rad = np.deg2rad(hatch_line_angle_deg)
        spacing = radius * hatch_spacing_ratio
        max_dist = np.sqrt(2 * radius**2) * 1.5

        for i in np.arange(-max_dist, max_dist, spacing):
            p1 = np.array([-max_dist, i])
            p2 = np.array([max_dist, i])

            cos_theta = np.cos(angle_rad)
            sin_theta = np.sin(angle_rad)

            rotated_p1_x = center_x + p1[0] * cos_theta - p1[1] * sin_theta
            rotated_p1_y = center_y + p1[0] * sin_theta + p1[1] * cos_theta

            rotated_p2_x = center_x + p2[0] * cos_theta - p2[1] * sin_theta
            rotated_p2_y = center_y + p2[0] * sin_theta + p2[1] * cos_theta

            line_artist, = ax.plot(
                [rotated_p1_x, rotated_p2_x],
                [rotated_p1_y, rotated_p2_y],
                color=hatch_line_color,
                linewidth=hatch_line_width,
                zorder=zorder_hatch,
                **kwargs # 允许传入额外的绘图参数
            )
            line_artist.set_clip_path(circle) # 确保阴影线被裁剪在圆内

    # 3. 绘制标签
    drawn_text = draw_vertex_label(ax=ax, vertex=vertex, current_label_props=current_label_props, use_relative_unit=use_relative_unit, **kwargs)

    return drawn_vertex, drawn_text




def draw_line_label(ax : plt.Axes, line : Line, current_label_text_options, use_relative_unit : bool = True, **kwargs):
    if not line.label or line.hidden_label:
        if not line.label:            # print(f"Line {line.id} has no label, skipping")
            return
        print(f"Line {line.id} is hidden, skipping")
        return

    if 'pre_render' in kwargs and kwargs['pre_render']:
        current_label_text_options['alpha'] = 0
        kwargs.pop('pre_render', None)



    # 绘制光子线的标签
    if line.label and not line.hidden_label:
        plot_points = line.plot_points
        mid_idx = len(plot_points) // 2
        label_x = (plot_points[mid_idx] + line.label_offset[0])[0]
        label_y = (plot_points[mid_idx] + line.label_offset[1])[1]

        # --- 新增的可见性检查 ---
        # xlim = ax.get_xlim()
        # ylim = ax.get_ylim()
        # print("\n***************************\n")
        # print(f"Label {line.label} x={label_x}, y={label_y}, xlim={xlim}, ylim={ylim}")
        # print(f"canvas xlim={ax.get_xbound()}, ylim={ax.get_ybound()}")
        # print(f"line label {line.label}, in range? {'Yes' if xlim[0] <= label_x <= xlim[1] and ylim[0] <= label_y <= ylim[1] else 'No'}")
        # if not ((xlim[0] <= label_x <= xlim[1]) and ylim[0] <= label_y <= ylim[1]):
        #     # 如果标签位置不在当前视图范围内，则跳过绘制
        #     print(f"Label {line.label} out of range, skipping")
        #     return
        # ------------------------
        if line.is_selected:
            current_label_text_options['color'] = highlight_color
            current_label_text_options['zorder'] = current_label_text_options.get('zorder', 1) + 10
            current_label_text_options['fontsize'] = current_label_text_options.get('fontsize', 12) * 1.5 # 增大字体

        label_in_latex = str2latex(line.label)
        current_label_text_options = convert_props_from_data(ax, current_label_text_options, use_relative_unit=use_relative_unit)
        drawn_text = ax.text(label_x,
                label_y,
                label_in_latex,
                **current_label_text_options, **kwargs)
        return drawn_text


def draw_vertex_label(ax :plt.Axes, vertex : Vertex, current_label_props,  use_relative_unit: bool = True, **kwargs):
    # 绘制标签
    if (vertex.label and not vertex.hidden_vertex and not vertex.hidden_label) or vertex.is_selected:
        label_x = vertex.x + vertex.label_offset[0]
        label_y = vertex.y + vertex.label_offset[1]

        # --- 新增的可见性检查 ---
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        # print(f"xlim: {xlim}")
        if not (xlim[0] <= label_x <= xlim[1] and ylim[0] <= label_y <= ylim[1]):
            # 如果标签位置不在当前视图范围内，则跳过绘制
            return
        # ------------------------
        current_label_props = convert_props_from_data(ax, current_label_props, use_relative_unit=use_relative_unit)
        label_in_latex = str2latex(vertex.label)
        drawn_text = ax.text(
            label_x,
            label_y,
            label_in_latex ,
            **current_label_props, # 使用调整后的标签属性
            **kwargs
        )
        return drawn_text


def draw_text_element(ax: plt.Axes, text_element: TextElement, use_relative_unit: bool = True,alpha=1, **kwargs) -> Text:
    """
    绘制 TextElement 对象的文本标签。

    Args:
        ax: Matplotlib Axes 对象。
        text_element: TextElement 对象，包含文本内容和位置。
        use_relative_unit: 是否使用相对单位进行尺寸转换。
        **kwargs: 其他绘图参数。

    Returns:
        绘制的 Text 对象。
    """
    
    if not text_element.text :
        return None


    # 获取当前文本属性并转换单位
    current_text_props = text_element.to_matplotlib_kwargs()
    current_text_props = convert_props_from_data(ax, current_text_props, use_relative_unit=use_relative_unit)

    if text_element.is_selected:
        # 如果有缩放倍数，调整字体大小
        current_text_props = get_highlighted_props(current_text_props)

    drawn_text = ax.text(alpha=alpha, **current_text_props)
    return drawn_text




def convert_props_from_data(ax: plt.Axes, props: Union[Dict[str, Any], float, int], prop_name : Optional[str] = None, use_relative_unit: bool = True) -> Union[Dict[str, Any], float, int]:
    """
    自动将指定的尺寸属性从数据单位转换为 Matplotlib 的绘图单位。
    此函数可以处理单个属性值或一个属性字典。

    Args:
        ax: Matplotlib Axes 对象。
        props: 包含需要转换的属性（数据单位）的字典，或者一个需要转换的浮点/整数值。
        use_relative_unit: 如果为 False，则直接返回原始值，不进行转换。

    Returns:
        一个包含转换后属性的新字典，或者一个转换后的值，取决于输入类型。
    """
    if not use_relative_unit:
        return props

    # 判断输入是字典还是单个值
    is_dict = isinstance(props, dict)
    
    # 获取转换因子（每数据单位对应的像素数）
    fig = ax.figure
    if fig is None:
        return props
    
    bbox = ax.get_position()
    fig_width_inch, _ = fig.get_size_inches()
    dpi = fig.dpi
    ax_width_px = bbox.width * fig_width_inch * dpi
    xlim = ax.get_xlim()
    data_range_x = xlim[1] - xlim[0]
    # print(f"ax_width_px: {ax_width_px}, data_range_x: {data_range_x}, dpi: {dpi}")
    
    # 避免除以零的错误
    if data_range_x == 0:
        return props
        
    px_per_data = ax_width_px / data_range_x
    scale_factor = px_per_data / dpi  # 每数据单位对应的像素数除以 DPI 得到每数据单位对应的 pt
    # print(f"px_per_data: {px_per_data}, dpi: {dpi}")

    # 定义需要转换的属性键
    # 这里我们只区分字体相关和非字体相关的属性
    fontsize_keys = {'fontsize', 'size'}
    other_size_keys = {'s', 'markersize', 'linewidth', 'markeredgewidth', 'elinewidth', 'mutation_scale', 'inner_linewidth',
                       'outer_linewidth'}
    
    def _convert_value(key: str, value: Union[float, int]):
        """内部函数，用于执行单个值的转换"""
        if value is None or not isinstance(value, (int, float)):
            return value
        if key in fontsize_keys or key in other_size_keys:
            # print(f"Converting {key}: {value} -> {value * scale_factor} (scale factor: {scale_factor})")
            return value * scale_factor
        else:
            # 如果不是需要转换的属性，直接返回原值
            # print(f"DEBUG: Skipping conversion for {key}: {value} (not a size property)")
            return value

    if is_dict:
        # 如果输入是字典，遍历每个键值对并转换
        adjusted_props = props.copy()
        for key, value in adjusted_props.items():
            adjusted_props[key] = _convert_value(key, value)

        return adjusted_props
    else:
        # 如果输入是单个值，我们假设它是 'linewidth' 类型
        # 你可以根据实际情况修改这个假设，或者要求调用者提供类型信息
        if prop_name is not None:
            return _convert_value(prop_name, props)
        else:
            print(f'Single Item Should have prop_name, but got None')
            return props


def get_highlighted_props(original_props: dict) -> dict:
    """
    根据原始属性字典，智能地生成一个用于高亮的新属性字典。
    
    Args:
        original_props: 包含原始绘图属性的字典。
        
    Returns:
        一个新字典，包含用于高亮的调整后属性。
    """
    # 定义高亮的颜色，你可以根据需要修改
    highlight_color = 'red' 

    highlighted_props = original_props.copy()
    
    # 所有元素都通用的高亮属性
    highlighted_props['color'] = highlight_color
    highlighted_props['zorder'] = original_props.get('zorder', 1) + 10
    
    # 针对不同元素类型，智能调整高亮效果
    # 增加线宽
    if 'linewidth' in original_props:
        highlighted_props['linewidth'] = original_props.get('linewidth', 1.5) * 1.5 + 3
    
    # 增加散点图标记大小，或将字符串变为粗体
    if 's' in original_props:
        # 检查s是数值（用于scatter）还是字符串（用于文本）
        s_value = original_props['s']
        if isinstance(s_value, (int, float)):
            highlighted_props['s'] = s_value * 1.5 + 20
        elif isinstance(s_value, str):
            # 将字体变为粗体
            highlighted_props['fontweight'] = 'bold'
    
    # 增加常规标记大小
    if 'markersize' in original_props:
        highlighted_props['markersize'] = original_props.get('markersize', 6) * 1.5 + 3
        
    # 增加字体大小
    if 'fontsize' in original_props:
        highlighted_props['fontsize'] = original_props.get('fontsize', 10) * 1.2
    
    # 增加边缘线宽
    if 'markeredgewidth' in original_props:
        highlighted_props['markeredgewidth'] = original_props.get('markeredgewidth', 1) * 1.5 + 1.5
    
    return highlighted_props


def draw_arrow(ax: plt.Axes, start: Tuple[float, float], end: Tuple[float, float],
               arrow_filled: bool = False, arrow_size: float = 1.0, alpha: float = 1.0,
               arrow_line_width: Optional[float] = None, arrow_style = 'fishtail', **kwargs):
    """
    在给定的 Axes 上绘制一个箭头。
    """
    # if start == end:
    #     return None
    drawn_arrow = None
    # print(f"DEBUG: draw_arrow() start: {start}, end: {end}, arrow_style: {arrow_style}, arrow_alpha: {alpha}")
    
    # 从 kwargs 获取参数，并设置默认值
    zorder = kwargs.get('zorder', 10)
    base_facecolor = kwargs.get('facecolor', 'black')
    base_edgecolor = kwargs.get('edgecolor', 'black')
    is_selected = kwargs.get('is_selected', False)
    mutation_scale = kwargs.get('mutation_scale', 50)
    
    mutation_scale = convert_props_from_data(ax, mutation_scale, prop_name='mutation_scale', use_relative_unit=True)

    # 如果选中，应用高亮颜色和大小变化
    if is_selected:
        highlight_color = 'red'  # 假设高亮颜色是红色
        base_facecolor = highlight_color
        base_edgecolor = highlight_color
        mutation_scale = mutation_scale * 1.5

    # 核心改动：将 alpha 值应用到颜色上
    # mcolors.to_rgba() 将颜色值和 alpha 值组合成 RGBA 格式
    facecolor = mcolors.to_rgba(base_facecolor, alpha)
    edgecolor = mcolors.to_rgba(base_edgecolor, alpha)

    if arrow_style == 'fishtail' or arrow_style == None:
        arrow_angle = kwargs.get('arrow_angle', 20)
        tail_angle = kwargs.get('arrow_tail_angle', 60)
        offset_ratio = kwargs.get('arrow_offset_ratio', 0.0)
        print(f"DEBUG: draw_arrow() arrow_angle: {arrow_angle}, tail_angle: {tail_angle}, offset_ratio: {offset_ratio}")

        drawn_arrow = ax.annotate(
            '', xy=end, xytext=start, zorder=zorder,
            ha='center', va='center',
            arrowprops=dict(
                arrowstyle=FishtailArrow(
                    arrow_angle=arrow_angle,
                    tail_angle=tail_angle,
                    offset_ratio=offset_ratio
                ),
                facecolor=facecolor,
                edgecolor=edgecolor,
                mutation_scale=mutation_scale, 
                shrinkA=0,  # 关闭起点收缩
                shrinkB=0   # 关闭终点收缩
            )
        )
    return drawn_arrow
    
        

def draw_line(ax: plt.Axes, line : Line, line_plot_options: dict, use_relative_unit: bool = True, **kwargs):
    line_plot_options = convert_props_from_data(ax, line_plot_options, use_relative_unit=use_relative_unit)
    # print(f"DEBUG : line_plot_options: {line_plot_options}")
    if line.linestyle == "Hollow" or line.linestyle == 'hollow':
        # 绘制空心线条
        draw_hollow_line(ax, line, line_plot_options, line_plot_options, **kwargs)
    elif line.linestyle in ['-', '--', '-.', ':']:
        # 绘制实线、虚线等
        # print(f"DEBUG : draw_line() : line_plot_options: {line_plot_options}")
        ax.plot(line.plot_points[:, 0], line.plot_points[:, 1], **line_plot_options)

def draw_hollow_line(ax: plt.Axes, line: Line, line_plot_options: dict, use_relative_unit: bool = True, **kwargs):   
    if not line.hollow_line_initialized:
        line._init_hollow_line(**kwargs)
    inner_line_zorder = line.inner_zorder if line.inner_zorder is not None else 5
    outer_line_zorder = line.outer_zorder if line.outer_zorder is not None else 4
    inner_color = line.inner_color if line.inner_color is not None else 'white'
    outer_color = line.outer_color if line.outer_color is not None else 'black'
    inner_linewidth = line.inner_linewidth if line.inner_linewidth is not None else 1.5
    outer_linewidth = line.outer_linewidth if line.outer_linewidth is not None else 2.0
    inner_linewidth = convert_props_from_data(ax, inner_linewidth, use_relative_unit=use_relative_unit, prop_name='inner_linewidth')
    outer_linewidth = convert_props_from_data(ax, outer_linewidth, use_relative_unit=use_relative_unit, prop_name='outer_linewidth')
    alpha = line_plot_options.get('alpha', 1.0)
    if line.is_selected:
        # 如果线被选中，调整绘图属性
        inner_color = 'white'  # 内层线条颜色
        outer_color = highlight_color
        inner_linewidth *= 1.5
        outer_linewidth *= 1.5 
        inner_line_zorder += 10
        outer_line_zorder += 10
    inner_line = ax.plot(line.plot_points[:, 0], line.plot_points[:, 1],
            color=inner_color, linewidth=inner_linewidth, linestyle='-', zorder=inner_line_zorder, alpha=alpha, **kwargs)

    # 绘制外层线条
    outer_line = ax.plot(line.plot_points[:, 0], line.plot_points[:, 1],
            color=outer_color, linewidth=outer_linewidth, linestyle='-', zorder=outer_line_zorder, alpha=alpha, **kwargs)

    return (inner_line[0], outer_line[0])