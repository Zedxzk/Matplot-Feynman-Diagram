import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from pygments import highlight
from feynplot_gui.debug_utils import cout
from feynplot.shared.common_functions import str2latex


# 导入你的核心模型类（如果这些函数直接依赖于 Line 和 Vertex 对象）
# 这些导入最好放在文件的顶部，以便清晰可见。
from feynplot.core.line import Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine, WPlusLine, WMinusLine, ZBosonLine
from feynplot.core.vertex import Vertex

# 导入生成路径的方法
from feynplot.core.gluon_methods import generate_gluon_helix # 假设你正在使用这个来获取胶子路径
from feynplot.core.photon_methods import generate_photon_wave
from feynplot.core.WZ_methods import generate_WZ_zigzag
from feynplot.core.fermion_methods import generate_fermion_line
import mplhep as hep

from feynplot.drawing.fontSettings import *


highlight_color = 'red'

def draw_photon_wave(ax, line: PhotonLine, line_plot_options: dict, label_text_options: dict):
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
    wave_path = generate_photon_wave(line)
    x_wave, y_wave = wave_path[:, 0], wave_path[:, 1]

    # 绘制光子波的路径，使用调整后的属性
    ax.plot(x_wave, y_wave, **current_line_plot_options)

    # 绘制光子线的标签
    if line.label:
        mid_idx = len(x_wave) // 2
        # --- 修改这里：使用 str2latex ---
        label_in_latex = str2latex(line.label)
        ax.text(x_wave[mid_idx] + line.label_offset[0],
                y_wave[mid_idx] + line.label_offset[1],
                label_in_latex,
                **current_label_text_options)


def draw_gluon_line(ax, line: GluonLine, line_plot_options: dict, label_text_options: dict):
    print('Detected GluonLine') # 可以保留用于调试
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
    # 假设 line.get_plot_path() 会返回正确的路径
    bezire_path, helix_path = line.get_plot_path()
    x_helix, y_helix = helix_path[:, 0], helix_path[:, 1]

    # 绘制胶子线的路径
    ax.plot(x_helix, y_helix, **current_line_plot_options)
    # ax.plot(bezire_path[:, 0], bezire_path[:, 1], **current_line_plot_options)

    # 绘制胶子线的标签
    if line.label:
        mid_idx = len(x_helix) // 2
        # --- 修改这里：使用 str2latex ---
        label_in_latex = str2latex(line.label)
        ax.text(x_helix[mid_idx] + line.label_offset[0],
                y_helix[mid_idx] + line.label_offset[1],
                label_in_latex,
                **current_label_text_options)


def draw_WZ_zigzag_line(ax, line: Line, line_plot_options: dict, label_text_options: dict):
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()

    original_linewidth = current_line_plot_options.get('linewidth', 1.5)
    original_color = current_line_plot_options.get('color', 'black')
    original_zorder = current_line_plot_options.get('zorder', 1)

    # 调用 generate_WZ_zigzag 获取所有路径
    zigzag_path, bezier_base_path_for_zigzag, high_res_bezier_path = generate_WZ_zigzag(line, start_up=True)

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
    ax.plot(x_zig, y_zig, **current_line_plot_options)

    # --- 绘制标签（居中位置）---
    if line.label:
        mid_idx = len(bezier_base_path_for_zigzag) // 2
        label_x = bezier_base_path_for_zigzag[mid_idx, 0] + line.label_offset[0]
        label_y = bezier_base_path_for_zigzag[mid_idx, 1] + line.label_offset[1]

        # --- 修改这里：使用 str2latex ---
        label_in_latex = str2latex(line.label)
        ax.text(label_x,
                label_y,
                label_in_latex,
                **current_label_text_options)


def draw_fermion_line(ax, line: FermionLine, line_plot_options: dict, label_text_options: dict):
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()
    print(line)
    # from pprint import pprint

    cout(f"current_line_plot_options: {current_line_plot_options}")
    cout(f"current_label_text_options: {current_label_text_options}")
    # input()
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
    ax.plot(x, y, **current_line_plot_options)

    # --- 绘制箭头 ---
    if line.arrow and len(x) > 1:
        arrow_filled = getattr(line, 'arrow_filled', False)
        arrow_position = getattr(line, 'arrow_position', 0.5)
        arrow_size = getattr(line, 'arrow_size', 1.0)
        arrow_line_width = getattr(line, 'arrow_line_width', None)
        arrow_reversed = getattr(line, 'arrow_reversed', False)

        if len(x) < 2:
            return

        # 核心修正：根据 arrow_reversed 调整 arrow_position 的计算基准
        # 这里 arrow_position 通常是 0.0 到 1.0，表示从起点到终点的位置
        # 如果是 reversed，我们想让箭头朝向起点，但位置仍按从起点算
        # 比如 arrow_position = 0.53, arrow_reversed = True 意味着从终点往回 0.53 的位置指向起点
        # 但我们这里的 target_idx 是从 x 数组中取，x 是从起点到终点的顺序
        # 所以我们需要调整的是 `xy` 和 `xytext` 的顺序，而不是 `arrow_position` 本身

        # 计算箭头的目标索引（尖端应该指向的位置）
        # 使用 line.arrow_position 来确定点
        idx_tip = int(round(arrow_position * (len(x) - 1)))

        # 确保 idx_tip 和 idx_base 在有效范围内
        # idx_base 应该是构成箭头的 "尾巴" 部分
        # 如果箭头正向，p_base 在前，p_tip 在后
        # 如果箭头反向，p_tip 在前，p_base 在后
        if idx_tip == 0:
            idx_base = 1 # 确保能找到前一个点来确定方向
        elif idx_tip >= len(x) - 1:
            idx_base = len(x) - 2 # 确保能找到后一个点
        else:
            # 默认情况下，p_base 是 p_tip 的前一个点，用于确定方向
            idx_base = idx_tip - 1


        p_tip = (x[idx_tip], y[idx_tip])
        p_base = (x[idx_base], y[idx_base])

        # 根据 arrow_reversed 调整 annotate 的 xy 和 xytext
        # annotate 的箭头从 xytext 指向 xy
        if arrow_reversed:
            # 如果反转，箭头尖端在 p_base，箭头从 p_tip 指向 p_base
            xy = p_base
            xytext = p_tip
        else:
            # 正常方向，箭头尖端在 p_tip，箭头从 p_base 指向 p_tip
            xy = p_tip
            xytext = p_base

        # 根据 arrow_filled 设置 arrowstyle
        if arrow_filled:
            arrowstyle_str = f'-|>,head_width={0.06*arrow_size},head_length={0.1*arrow_size}' # 实心箭头
        else:
            arrowstyle_str = f'->,head_width={0.04*arrow_size},head_length={0.08*arrow_size}'

        # 设置箭头的线宽，如果未指定则使用线条的线宽
        arrow_lw = arrow_line_width if arrow_line_width is not None else \
                           current_line_plot_options.get('linewidth', 1.5)

        arrow_props = dict(
            arrowstyle=arrowstyle_str,
            linewidth=arrow_lw,
            color=current_line_plot_options.get('color', 'black'), # 箭头颜色与线颜色一致
            zorder=current_line_plot_options.get('zorder', 1) + 1 # 箭头比线高一层
        )

        ax.annotate(
            '', xy=xy, xytext=xytext, arrowprops=arrow_props
        )

    # --- 绘制标签 ---
    if line.label:
        mid_idx = len(fermion_path) // 2
        label_x = fermion_path[mid_idx, 0] + line.label_offset[0]
        label_y = fermion_path[mid_idx, 1] + line.label_offset[1]
        # --- 修改这里：使用 str2latex ---
        label_in_latex = str2latex(line.label)
        ax.text(label_x, label_y, label_in_latex, **current_label_text_options)


def draw_point_vertex(ax: plt.Axes, vertex: Vertex):
    # 复制字典以避免修改原始对象内部的配置
    current_scatter_props = vertex.get_scatter_properties().copy()
    current_label_props = vertex.get_label_properties().copy()
    print(f"current_scatter_props: {current_scatter_props}")
    print(f"current_label_props: {current_label_props}")

    # 移除冲突的参数
    if 'c' in current_scatter_props and 'color' in current_scatter_props:
        current_scatter_props.pop('c')  # 或者 pop('color')
    # 如果有 size 参数，替换成 s
    if 'size' in current_scatter_props:
        current_scatter_props['s'] = current_scatter_props.pop('size')


    original_size = current_scatter_props.get('s', 100)
    original_color = current_scatter_props.get('c', 'blue')
    original_edgecolor = current_scatter_props.get('edgecolor', original_color)
    original_linewidth = current_scatter_props.get('linewidth', 1.0)
    original_zorder = current_scatter_props.get('zorder', 2) # 顶点的默认 zorder 为 2

    # 如果顶点被选中，调整绘图属性
    if vertex.is_selected:
        current_scatter_props['s'] = original_size * 1.5 # 放大
        current_scatter_props['c'] = highlight_color # 变色
        current_scatter_props['edgecolor'] = highlight_color
        current_scatter_props['linewidth'] = original_linewidth + 1.0
        current_scatter_props['zorder'] = original_zorder + 10 # 提高 Z-order

        # 标签也可能需要调整
        current_label_props['color'] = highlight_color
        current_label_props['zorder'] = original_zorder + 11

    # --- 修改这里：只绘制一次点状顶点 ---
    if not vertex.hidden_vertex:
        print(current_scatter_props)
        ax.scatter(vertex.x, vertex.y, **current_scatter_props)

    # 绘制标签
    if vertex.label and not vertex.hidden_vertex and not vertex.hidden_label:
        # --- 修改这里：使用 str2latex ---
        label_in_latex = str2latex(vertex.label)
        ax.text(
            vertex.x + vertex.label_offset[0],
            vertex.y + vertex.label_offset[1],
            label_in_latex ,
            # fontdict={'weight': "bold", 'style': "italic"},
            **current_label_props # 使用调整后的标签属性
        )


def draw_structured_vertex(ax: plt.Axes, vertex: Vertex):
    # 复制字典以避免修改原始对象内部的配置
    current_circle_props = vertex.get_circle_properties().copy()
    current_custom_hatch_props = vertex.get_custom_hatch_properties().copy()
    current_label_props = vertex.get_label_properties().copy()

    original_linewidth = current_circle_props.get('linewidth', 1.5)
    original_edgecolor = current_circle_props.get('edgecolor', 'black')
    original_zorder = current_circle_props.get('zorder', 2)

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
    circle = Circle(
        (vertex.x, vertex.y),
        **current_circle_props
    )
    ax.add_patch(circle)

    # 2. 绘制阴影线 (如果使用自定义模式)
    if vertex.use_custom_hatch:
        # 使用调整后的 custom_hatch_props
        hatch_line_color = current_custom_hatch_props['hatch_line_color']
        hatch_line_width = current_custom_hatch_props['hatch_line_width']
        hatch_line_angle_deg = current_custom_hatch_props['hatch_line_angle_deg']
        hatch_spacing_ratio = current_custom_hatch_props['hatch_spacing_ratio']

        radius = vertex.structured_radius
        center_x = vertex.x
        center_y = vertex.y
        # 使用调整后的 zorder
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
                zorder=zorder_hatch # 使用调整后的阴影线 zorder
            )
            line_artist.set_clip_path(circle)

    # 3. 绘制标签
    if vertex.label:
        # --- 修改这里：使用 str2latex ---
        label_in_latex = str2latex(vertex.label)
        ax.text(
            vertex.x + vertex.label_offset[0],
            vertex.y + vertex.label_offset[1],
            label_in_latex,
            **current_label_props # 使用调整后的标签属性
        )