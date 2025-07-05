from feynplot.core.line import Line, WPlusLine, WMinusLine, ZBosonLine, FermionLine, AntiFermionLine, PhotonLine, GluonLine
from typing import Optional
import numpy as np
from feynplot.core.WZ_methods import generate_WZ_zigzag
from feynplot.core.fermion_methods import generate_fermion_line
from feynplot.core.gluon_methods import generate_gluon_helix, generate_gluon_bezier
from feynplot.core.photon_methods import generate_photon_wave
from feynplot.core.fermion_methods import cubic_bezier

def update_line_plot_points(line: Line):
    """
    根据给定的 Line 实例的类型，计算并设置其 plot_points 属性。

    这个函数会根据线条的具体子类（如 FermionLine, WPlusLine 等）
    调用相应的绘图点生成函数，并将生成的路径点赋值给 line.plot_points。

    Args:
        line (Line): 要更新 plot_points 的 Line 实例。

    Raises:
        ValueError: 如果线条的起始或结束顶点未设置。
        TypeError: 如果传入的不是 Line 实例或其子类。
    """
    if not isinstance(line, Line):
        raise TypeError("The 'line' argument must be an instance of Line or its subclass.")
    
    if line.v_start is None or line.v_end is None:
        raise ValueError(f"Line '{line.id}' has unassigned vertices. Cannot generate plot_points without start and end points.")

    plot_points_array: Optional[np.ndarray] = None

    if isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
        # 对于 W+, W-, Z 波色子线，调用 generate_WZ_zigzag
        # generate_WZ_zigzag 可能会返回多个数组，我们通常只关心第一个（实际绘制路径）
        # start_up 是 generate_WZ_zigzag 特有的参数，从 line 实例中获取或使用默认值
        zigzag_path, _, _ = generate_WZ_zigzag(line, start_up=getattr(line, 'start_up', True))
        plot_points_array = zigzag_path
    elif isinstance(line, (FermionLine, AntiFermionLine)):
        # 对于费米子线和反费米子线
        plot_points_array = generate_fermion_line(line)
    elif isinstance(line, PhotonLine):
        # 对于光子线
        plot_points_array = generate_photon_wave(line)
    elif isinstance(line, GluonLine):
        # 对于胶子线，可以根据你的需求选择调用 helix 或 bezier
        plot_points_array = generate_gluon_helix(line) # 或者 generate_gluon_bezier(line)
    else:
        # 对于其他通用 Line 类型或未特殊处理的子类，使用默认的贝塞尔路径
        start_point_coords = (line.v_start.x, line.v_start.y)
        end_point_coords = (line.v_end.x, line.v_end.y)
        xs, ys = cubic_bezier(np.array(start_point_coords), np.array(end_point_coords),
                              angle_out=getattr(line, 'angleOut', 0.0),
                              angle_in=getattr(line, 'angleIn', 0.0),
                              offset_ratio=getattr(line, 'bezier_offset', 0.0)
                              )
        plot_points_array = np.column_stack((xs, ys))
    
    # 将 NumPy 数组转换为列表的元组，并赋值给 line.plot_points
    if plot_points_array is not None:
        line.plot_points = plot_points_array.tolist()
    else:
        line.plot_points = [] # 如果没有生成点，则清空