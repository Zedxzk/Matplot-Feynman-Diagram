import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from feynplot_gui.debug_utils import cout
from feynplot.shared.common_functions import str2latex
from feynplot.core.extra_text_element import TextElement
from matplotlib.text import Text
from matplotlib.axes import Axes
from feynplot.default_settings.default_settings import renderer_default_settings

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

def draw_photon_wave(ax, line: PhotonLine, line_plot_options: dict, label_text_options: dict, zoom_times: int = 0):
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
    drawn_line = ax.plot(x_wave, y_wave, **current_line_plot_options)
    line.set_plot_points(x_wave, y_wave)
    drwan_text = draw_line_label(ax, line, label_text_options, zoom_times) # 绘制标签
    return drawn_line, drwan_text
        

def draw_gluon_line(ax, line: GluonLine, line_plot_options: dict, label_text_options: dict, zoom_times: int = 0):
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
    drawn_line = ax.plot(x_helix, y_helix, **current_line_plot_options)
    line.set_plot_points(x_helix, y_helix)

    drawn_text = draw_line_label(ax, line, label_text_options) # 绘制标签
    return drawn_line, drawn_text


def draw_WZ_zigzag_line(ax, line: Line, line_plot_options: dict, label_text_options: dict, zoom_times: int = 0):
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
    drawn_line = ax.plot(x_zig, y_zig, **current_line_plot_options)
    line.set_plot_points(x_zig, y_zig)
    

    drawn_text = draw_line_label(ax, line, label_text_options) # 绘制标签
    return drawn_line, drawn_text


def draw_fermion_line(ax, line: FermionLine, line_plot_options: dict, label_text_options: dict, zoom_times: int = 0):
    current_line_plot_options = line_plot_options.copy()
    current_label_text_options = label_text_options.copy()

    cout(f"current_line_plot_options: {current_line_plot_options}")
    cout(f"current_label_text_options: {current_label_text_options}")

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
    drawn_line = ax.plot(x, y, **current_line_plot_options)
    line.set_plot_points(x, y)
    # from pprint import pprint
    # points = line.get_line_plot_points()[:10]
    # formatted_points = [f"({x:.3f}, {y:.3f})" for (x, y) in points]
    # pprint(f"fermion_path: {formatted_points}")

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

        if arrow_filled:
            arrowstyle_str = f'-|>,head_width={0.06*arrow_size},head_length={0.1*arrow_size}'
        else:
            arrowstyle_str = f'->,head_width={0.04*arrow_size},head_length={0.08*arrow_size}'

        arrow_lw = arrow_line_width if arrow_line_width is not None else \
                           current_line_plot_options.get('linewidth', 1.5)

        arrow_props = dict(
            arrowstyle=arrowstyle_str,
            linewidth=arrow_lw,
            color=current_line_plot_options.get('color', 'black'),
            zorder=current_line_plot_options.get('zorder', 1) + 1
        )

        ax.annotate(
            '', xy=xy, xytext=xytext, arrowprops=arrow_props
        )

    drawn_text = draw_line_label(ax, line, label_text_options, zoom_times) # 绘制标签
    return drawn_line, drawn_text


def draw_point_vertex(ax: plt.Axes, vertex: Vertex, zoom_times: int = 0):
    # 复制字典以避免修改原始对象内部的配置
    current_scatter_props = vertex.get_scatter_properties().copy()
    current_label_props = vertex.get_label_properties().copy()
    cout(f"current_scatter_props: {current_scatter_props}")
    cout(f"current_label_props: {current_label_props}")

    # 移除冲突的参数
    if 'c' in current_scatter_props and 'color' in current_scatter_props:
        current_scatter_props.pop('c')
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

    # --- 绘制点状顶点 ---
    if not vertex.hidden_vertex or vertex.is_selected:
        cout(current_scatter_props)
        ax.scatter(vertex.x, vertex.y, **current_scatter_props)

    # 绘制标签
    drawn_text = draw_vertex_label(ax, vertex, current_label_props, zoom_times)

    # if (vertex.label and not vertex.hidden_vertex and not vertex.hidden_label) or vertex.is_selected:
    #     label_x = vertex.x + vertex.label_offset[0]
    #     label_y = vertex.y + vertex.label_offset[1]

    #     # --- 新增的可见性检查 ---
    #     xlim = ax.get_xlim()
    #     ylim = ax.get_ylim()
    #     # print(f"xlim: {xlim}")
    #     if not (xlim[0] <= label_x <= xlim[1] and ylim[0] <= label_y <= ylim[1]):
    #         # 如果标签位置不在当前视图范围内，则跳过绘制
    #         return
    #     # ------------------------

    #     label_in_latex = str2latex(vertex.label)
    #     drawn_text = ax.text(
    #         label_x,
    #         label_y,
    #         label_in_latex ,
    #         **current_label_props # 使用调整后的标签属性
    #     )
    #     return drawn_text
    return drawn_text


def draw_structured_vertex(ax: plt.Axes, vertex: Vertex, zoom_times : int = 0):
    # 复制字典以避免修改原始对象内部的配置
    current_circle_props = vertex.get_circle_properties().copy()
    current_custom_hatch_props = vertex.get_custom_hatch_properties().copy()
    current_label_props = vertex.get_label_properties().copy()

    original_linewidth = current_circle_props.get('linewidth', 1.5)
    original_edgecolor = current_circle_props.get('edgecolor', 'black')
    original_zorder = current_circle_props.get('zorder_structured', 10)

    if vertex.hidden_vertex and not vertex.is_selected:
        return

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
        ax.add_patch(circle)
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
                zorder=zorder_hatch
            )
            line_artist.set_clip_path(circle) # 确保阴影线被裁剪在圆内

    # 3. 绘制标签
    drawn_text = draw_vertex_label(ax=ax, vertex=vertex, current_label_props=current_label_props, zoom_times=zoom_times)
    # if (vertex.label and not vertex.hidden_label and not vertex.hidden_vertex) or  vertex.is_selected: # 只有当圆圈可见时才绘制标签
    #     label_x = vertex.x + vertex.label_offset[0]
    #     label_y = vertex.y + vertex.label_offset[1]

    #     # --- 新增的可见性检查 (针对标签) ---
    #     # 即使圆圈可见，标签自身也可能超出视图，所以这里再检查一次更精确
    #     xlim = ax.get_xlim()
    #     ylim = ax.get_ylim()
    #     if not (xlim[0] <= label_x <= xlim[1] and ylim[0] <= label_y <= ylim[1]):
    #         return # 如果标签位置不在当前视图范围内，则跳过绘制
    #     # ------------------------
        
    #     label_in_latex = str2latex(vertex.label)
    #     drawn_text = ax.text(
    #         label_x,
    #         label_y,
    #         label_in_latex,
    #         **current_label_props
    #     )
    return drawn_text

def get_diagram_view_limits(
    ax: plt.Axes, # Axes 对象仍然需要，尽管我们不直接用它来测量文本尺寸
    vertices: List[Vertex],
    lines: List[Line],
    drawn_texts : Optional[List[Text]] = None
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    根据顶点和线列表，计算并返回合适的画布视图范围 (xlim, ylim)。
    遍历所有顶点、线的完整路径以及标签的锚点位置，找到 x 和 y 的最小/最大值。
    """
    all_x: List[float] = []
    all_y: List[float] = []

    # 1. 考虑所有顶点的中心坐标
    for v in vertices:
        all_x.append(v.x)
        all_y.append(v.y)
        
        # Determine label properties for the current vertex (still useful for drawing later)
        # vertex_label_props = v.get_label_properties() # This line is no longer strictly needed for limits calculation
        
        # If StructuredVertex, consider its radius
        if hasattr(v, 'structured_radius') and v.structured_radius is not None and v.is_structured:
            radius = v.structured_radius
            all_x.extend([v.x - radius, v.x + radius])
            all_y.extend([v.y - radius, v.y + radius])
        size2pix = 0.002
        if not v.hidden_vertex:
            # print("v.size", v.size)
            all_x.extend([v.x + float(v.size) * size2pix, v.x - float(v.size) * size2pix])
            all_y.extend([v.y + float(v.size) * size2pix, v.y - float(v.size) * size2pix])

        # 考虑顶点的标签锚点位置
        if v.label and not v.hidden_label:
            label_origin_x = v.x + v.label_offset[0]
            label_origin_y = v.y + v.label_offset[1]
            
            # **核心修改：只添加标签的锚点位置**
            all_x.append(label_origin_x)
            all_y.append(label_origin_y)

    # 2. 考虑所有线条的完整路径点
    for line in lines:
        path = np.array([]) # Initialize as empty path

        # Get path points based on line type
        if isinstance(line, PhotonLine):
            path = generate_photon_wave(line)
        elif isinstance(line, GluonLine):
            _, path = line.get_plot_path()
        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            path, _, _ = generate_WZ_zigzag(line, start_up=True)
        elif isinstance(line, FermionLine):
            path = generate_fermion_line(line)
        else: # Default straight line or other unknown line type
            # Assuming line.v_start and line.v_end are Vertex objects (not just IDs)
            start_v = next((v_item for v_item in vertices if v_item.id == line.v_start.id), None)
            end_v = next((v_item for v_item in vertices if v_item.id == line.v_end.id), None)
            if start_v and end_v:
                path = np.array([[start_v.x, start_v.y],
                                 [end_v.x, end_v.y]])

        if path.size > 0:
            all_x.extend(path[:, 0])
            all_y.extend(path[:, 1])

        # 考虑线的标签锚点位置
        if line.label and not line.hidden_label:
            # 标签的基准位置通常是线的中点加上偏移
            mid_point_x, mid_point_y = 0, 0
            if path.size > 0:
                mid_point_x = path[:, 0].mean()
                mid_point_y = path[:, 1].mean()
            elif start_v and end_v: # If path is empty, fall back to midpoint of line endpoints
                mid_point_x = (start_v.x + end_v.x) / 2
                mid_point_y = (start_v.y + end_v.y) / 2
            # else: mid_point_x, mid_point_y remain 0,0 - not ideal, but fallback for unlinked lines

            label_origin_x = mid_point_x + line.label_offset[0]
            label_origin_y = mid_point_y + line.label_offset[1]

            # **核心修改：只添加标签的锚点位置**
            all_x.append(label_origin_x)
            all_y.append(label_origin_y)


    # --- 【新增】3. 处理已绘制的文本对象 ---
    # if drawn_texts:
    #     for text_obj in drawn_texts:
    #         # 获取文本对象的边界框
    #         # 必须先绘制 canvas 才能获得正确的边界框
    #         bbox = text_obj.get_window_extent().transformed(ax.transData.inverted())
    #         # print("bbox:", bbox.x0, bbox.x1, bbox.y0, bbox.y1)
    #         # for corner_name, (x, y) in corners.items():
    #         # 将边界框的四个角点坐标加入列表
    #         all_x.append(bbox.x0)
    #         all_x.append(bbox.x1)
    #         all_y.append(bbox.y0)
    #         all_y.append(bbox.y1)


    # If no elements, return default view
    if not all_x or not all_y:
        return (-5.0, 5.0), (-5.0, 5.0)

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    # Add a margin to prevent elements from touching the border
    padding_ratio = 0.02
    
    # Calculate current content width and height
    content_width = max_x - min_x
    content_height = max_y - min_y

    # Ensure a minimum size for the content, even if it's just a single point
    min_content_size = 2.0 
    if content_width < min_content_size:
        mid_x = (max_x + min_x) / 2
        min_x = mid_x - min_content_size / 2
        max_x = mid_x + min_content_size / 2
        content_width = min_content_size # Update width for padding calculation

    if content_height < min_content_size:
        mid_y = (max_y + min_y) / 2
        min_y = mid_y - min_content_size / 2
        max_y = mid_y + min_content_size / 2
        content_height = min_content_size # Update height for padding calculation

    # Apply padding
    padding_x = content_width * padding_ratio
    padding_y = content_height * padding_ratio

    new_xlim = (min_x - padding_x, max_x + padding_x)
    new_ylim = (min_y - padding_y, max_y + padding_y)
    
    return new_xlim, new_ylim



def draw_line_label(ax : plt.Axes, line : Line, current_label_text_options, zoom_times : int = 0):
    if not line.label or line.hidden_label:
        print(f"Line {line.id} is hidden, skipping")
        return

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
        
        label_in_latex = str2latex(line.label)
        current_label_text_options = get_fontsize_from_data_units(ax, current_label_text_options)
        drawn_text = ax.text(label_x,
                label_y,
                label_in_latex,
                **current_label_text_options)
        return drawn_text


def draw_vertex_label(ax :plt.Axes, vertex : Vertex, current_label_props, zoom_times : int = 0):
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
        current_label_props = get_fontsize_from_data_units(ax, current_label_props)
        label_in_latex = str2latex(vertex.label)
        drawn_text = ax.text(
            label_x,
            label_y,
            label_in_latex ,
            **current_label_props # 使用调整后的标签属性
        )
        return drawn_text




def get_fontsize_from_data_units(
    ax: plt.Axes,
    text_properties: dict
) -> dict:
    """
    从字典中提取字体大小并根据数据单位进行调整。
    
    Args:
        ax: Matplotlib 的 Axes 对象。
        text_properties: 包含文本属性的字典，可能包含 'fontsize' 或 'size' 键。
        
    Returns:
        调整后的文本属性字典。
    """
    # 复制字典以避免修改原始字典
    adjusted_props = text_properties.copy()
    
    fig = ax.figure
    if fig is None:
        return adjusted_props  # 如果没有 figure，返回原始属性

    # fig_width_inch, fig_height_inch = fig.get_size_inches()
    # print(f"Figure size in inches: {fig_width_inch} x {fig_height_inch}")
    xlim = ax.get_xlim()
    data_range = xlim[1] - xlim[0]
    print(f"Data range in x-axis: {data_range}")
    
    if data_range == 0:
        return adjusted_props  # 如果数据范围为0，返回原始属性

    # 提取字体大小
    fontsize = None
    if 'fontsize' in adjusted_props:
        fontsize = adjusted_props['fontsize']
    elif 'size' in adjusted_props:
        fontsize = adjusted_props['size']
        # 将 size 转换为 fontsize
        adjusted_props['fontsize'] = adjusted_props.pop('size')
    
    if fontsize is not None:
        # 计算调整后的字体大小
        target_pixels = 12 * fontsize / data_range
        adjusted_props['fontsize'] = target_pixels
    
    return adjusted_props


