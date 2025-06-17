# plot_functions.py (或 feynplot/drawing/vertex_drawers.py)


import numpy as np
from feynplot.core.gluon_methods import generate_gluon_helix, generate_gluon_bezier
from feynplot.core.photon_methods import generate_photon_wave
from feynplot.core.WZ_methods import generate_WZ_zigzag
from feynplot.core.fermion_methods import generate_fermion_line
from feynplot.core.vertex import Vertex 

def draw_photon_wave(ax, line, line_plot_options, label_text_options):
    # from feynplot.core.photon_methods import generate_photon_wave  # 确保在这里有这个导入
    # 直接调用 generate_photon_wave 函数来获取路径点
    wave_path = generate_photon_wave(line)
    x_wave, y_wave = wave_path[:, 0], wave_path[:, 1]

    # 绘制光子波的路径
    ax.plot(x_wave, y_wave, **line_plot_options)

    # 绘制光子线的箭头 (如果需要)
    # if line.arrow and len(x_wave) > 1:
    #     arrow_props = dict(arrowstyle='->',
    #                        linewidth=line_plot_options.get('linewidth', 1.5),
    #                        color=line_plot_options.get('color', 'black'))
    #     # 箭头绘制逻辑可以复用普通线的 ax.arrow 方式
    #     p_start = (x_wave[0], y_wave[0])
    #     p_end = (x_wave[-1], y_wave[-1])
    #     length = np.sqrt((p_end[0] - p_start[0])**2 + (p_end[1] - p_start[1])**2)
    #     if length > 0:
    #         head_length_abs = 0.08
    #         head_width_abs = 0.08
    #         if length < head_length_abs * 2:
    #             head_length_abs = length / 2
    #             head_width_abs = length / 2
    #         arrow_dx = (p_end[0] - p_start[0]) * (1 - head_length_abs / length)
    #         arrow_dy = (p_end[1] - p_start[1]) * (1 - head_length_abs / length)
    #         ax.arrow(p_start[0], p_start[1], arrow_dx, arrow_dy,
    #                  head_width=head_width_abs, head_length=head_length_abs,
    #                  fc=arrow_props['color'], ec=arrow_props['color'],
    #                  linewidth=arrow_props['linewidth'],
    #                  length_includes_head=True)

    # 绘制光子线的标签
    if line.label:
        mid_idx = len(x_wave) // 2
        ax.text(x_wave[mid_idx] + line.label_offset[0],
                y_wave[mid_idx] + line.label_offset[1],
                line.label,
                **label_text_options)

def draw_gluon_line(ax, line, line_plot_options, label_text_options):
    print('Detected GluonLine')
    # Helix path (D-track)
    # Ensure line.get_plot_path() correctly calls generate_gluon_helix internally
    helix_path = line.get_plot_path()
    x_helix, y_helix = helix_path[:, 0], helix_path[:, 1]

    # Draw the helix path using all plot options
    ax.plot(x_helix, y_helix, **line_plot_options)

    # Draw arrow (at the end of the helix)
    # if line.arrow and len(x_helix) > 1:
    #     # Arrow properties inherit from line, but can be overridden
    #     arrow_props = dict(arrowstyle='->',
    #                        linewidth=line_plot_options.get('linewidth', 1.5),
    #                        color=line_plot_options.get('color', 'black'))
    #     # You can merge specific arrow properties from line.plotConfig if needed
    #     # e.g., arrow_props.update(line.plotConfig.get('arrowprops', {}))
    #     # Calculate arrow position and direction
    #     p_end = (x_helix[-1], y_helix[-1])
    #     p_base = (x_helix[-2], y_helix[-2])  # Arrow base, using the second to last point
    #     ax.annotate(
    #         '',
    #         xy=p_end,
    #         xytext=p_base,
    #         arrowprops=arrow_props
    #     )

    # Draw label near the midpoint of the helix
    if line.label:
        mid_idx = len(x_helix) // 2
        ax.text(x_helix[mid_idx] + line.label_offset[0],
                y_helix[mid_idx] + line.label_offset[1],
                line.label,
                **label_text_options)
        


def draw_WZ_zigzag_line(ax, line, line_plot_options, label_text_options):
    """
    在 Matplotlib 轴上绘制 W/Z 玻色子的锯齿线，以及其下方的两条贝塞尔基准线（一条用于对齐，一条高分辨率）。
    同时处理箭头的绘制和标签的放置。

    参数:
        ax: Matplotlib 的 Axes 对象。
        line: 一个 WZLine 实例，包含绘制所需的所有信息。
        line_plot_options: 一个字典，包含传递给 ax.plot() 的样式选项，用于锯齿线。
        label_text_options: 一个字典，包含传递给 ax.text() 的样式选项，用于标签。
    """
    # 调用 generate_WZ_zigzag，并正确解包其返回的三个路径
    # zigzag_path: 实际的锯齿路径
    # bezier_base_path_for_zigzag: 与锯齿路径点数相同的贝塞尔曲线，用于对齐和标签
    # high_res_bezier_path: 2000点的高分辨率贝塞尔曲线，用于背景显示
    zigzag_path, bezier_base_path_for_zigzag, high_res_bezier_path = generate_WZ_zigzag(line, start_up=True)
    
    # --- 绘制高分辨率贝塞尔曲线 (最底层，最平滑的背景线) ---
    high_res_bezier_plot_options = line_plot_options.copy()
    high_res_bezier_plot_options['linestyle'] = ':'  # 例如，点线
    high_res_bezier_plot_options['linewidth'] = line_plot_options.get('linewidth', 1.5) * 0.25 # 更细
    high_res_bezier_plot_options['color'] = 'lightgray' # 浅灰色，更不显眼
    high_res_bezier_plot_options['zorder'] = 0 # 确保在所有线的最底层

    ax.plot(high_res_bezier_path[:, 0], high_res_bezier_path[:, 1], **high_res_bezier_plot_options)

    # --- 绘制锯齿路径 (主要线条) ---
    x_zig, y_zig = zigzag_path[:, 0], zigzag_path[:, 1]
    ax.plot(x_zig, y_zig, **line_plot_options) # 使用原始的 line_plot_options 绘制锯齿线

    # ax.plot(bezier_base_path_for_zigzag[:, 0], bezier_base_path_for_zigzag[:, 1])

    # --- 绘制标签（居中位置）---
    # 标签现在始终放置在与锯齿线点数相同的贝塞尔基准路径上，以保证位置的稳定性和可见性
    if line.label:
        mid_idx = len(bezier_base_path_for_zigzag) // 2 
        
        label_x = bezier_base_path_for_zigzag[mid_idx, 0] + line.label_offset[0]
        label_y = bezier_base_path_for_zigzag[mid_idx, 1] + line.label_offset[1]
        
        ax.text(label_x,
                label_y,
                line.label,
                **label_text_options)


def draw_fermion_line(ax, line, line_plot_options, label_text_options):
    """
    在 Matplotlib 轴上绘制费米子线，包括在中间绘制箭头和标签。
    支持控制箭头的大小、是否实心、线宽、位置和方向。
    """
    fermion_path = generate_fermion_line(line)
    x, y = fermion_path[:, 0], fermion_path[:, 1]
    
    # 绘制费米子线本身
    ax.plot(x, y, **line_plot_options)

    # --- 绘制箭头 ---
    if line.arrow and len(x) > 1:
        arrow_filled = getattr(line, 'arrow_filled', False) # 默认改为 False
        arrow_position = getattr(line, 'arrow_position', 0.5)
        arrow_size = getattr(line, 'arrow_size', 1.0) # 保持为缩放因子
        arrow_line_width = getattr(line, 'arrow_line_width', None) # 新增获取箭头线宽
        arrow_reversed = getattr(line, 'arrow_reversed', False)

        if len(x) < 2:
            return 

        # 核心修正：根据 arrow_reversed 调整 arrow_position 的计算基准
        effective_arrow_position = arrow_position
        if arrow_reversed:
            arrow_position = 0.53
            effective_arrow_position = 1.0 - arrow_position # 如果反转，位置从终点开始算

        # 计算箭头的目标索引（尖端应该指向的位置）
        # 使用调整后的 effective_arrow_position
        target_idx = int(round(effective_arrow_position * (len(x) - 1)))
        
        # 确保 target_idx 在有效范围内，且能找到前后点来确定方向
        # 我们需要 target_idx 和 target_idx-1 两个点
        if target_idx == 0 and len(x) > 1:
            target_idx = 1 # 至少从第二个点开始取样，以便计算方向
        elif target_idx >= len(x) - 1 and len(x) > 1:
            target_idx = len(x) - 2 # 确保其前一个点 (target_idx-1) 存在

        # 确定箭头的尖端 (p_tip) 和基部 (p_base)
        # p_tip 始终是 arrow_position 对应的点，p_base 是其前一个点
        p_tip = (x[target_idx], y[target_idx])
        p_base = (x[target_idx - 1], y[target_idx - 1])

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

        # 设置箭头的线宽
        arrow_lw = arrow_line_width if arrow_line_width is not None else \
                   line_plot_options.get('linewidth', 1.5)

        arrow_props = dict(
            arrowstyle=arrowstyle_str,
            linewidth=arrow_lw, # 应用箭头线宽
            color=line_plot_options.get('color', 'black') # 箭头颜色与线颜色一致
        )

        ax.annotate(
            '', xy=xy, xytext=xytext, arrowprops=arrow_props
        )

    # --- 绘制标签 ---
    if line.label:
        mid_idx = len(fermion_path) // 2 
        label_x = fermion_path[mid_idx, 0] + line.label_offset[0]
        label_y = fermion_path[mid_idx, 1] + line.label_offset[1]
        ax.text(label_x, label_y, line.label, **label_text_options)



import matplotlib.pyplot as plt
from matplotlib.patches import Circle


def draw_point_vertex(ax: plt.Axes, vertex):
    """
    绘制一个普通的点状顶点。
    """
    scatter_props = vertex.get_scatter_properties()
    ax.scatter(vertex.x, vertex.y, **scatter_props)
    
    if vertex.label:
        label_props = vertex.get_label_properties()
        ax.text(
            vertex.x + vertex.label_offset[0], 
            vertex.y + vertex.label_offset[1], 
            vertex.label, 
            zorder=vertex.zorder + 1, 
            **label_props
        )

def draw_structured_vertex(ax: plt.Axes, vertex):
    """
    绘制一个带填充、边框和阴影的结构化圆形顶点。
    根据 Vertex.use_custom_hatch 决定使用内置hatch还是自定义阴影线。
    """
    # 1. 绘制圆圈主体
    circle_props = vertex.get_circle_properties()
    circle = Circle(
        (vertex.x, vertex.y),
        **circle_props 
    )
    ax.add_patch(circle)

    # 2. 绘制阴影线 (如果使用自定义模式)
    if vertex.use_custom_hatch:
        custom_hatch_props = vertex.get_custom_hatch_properties()
        
        hatch_line_color = custom_hatch_props['hatch_line_color']
        hatch_line_width = custom_hatch_props['hatch_line_width']
        hatch_line_angle_deg = custom_hatch_props['hatch_line_angle_deg']
        hatch_spacing_ratio = custom_hatch_props['hatch_spacing_ratio']
        
        radius = vertex.structured_radius
        center_x = vertex.x
        center_y = vertex.y
        zorder = vertex.zorder_structured

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
                zorder=zorder + 0.5 
            )
            # 关键：将线条裁剪到圆形内部
            line_artist.set_clip_path(circle) 

    # 3. 绘制标签
    if vertex.label:
        label_props = vertex.get_label_properties()
        ax.text(
            vertex.x + vertex.label_offset[0], 
            vertex.y + vertex.label_offset[1], 
            vertex.label, 
            zorder=vertex.zorder_structured + 1, # 标签在圆和阴影之上
            **label_props
        )