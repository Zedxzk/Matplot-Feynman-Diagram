import numpy as np
import math

# 假设 cubic_bezier 和 bezier_tangent 定义在 feynplot.core.bezier 中
from feynplot.core.bezier import cubic_bezier, bezier_tangent

def generate_WZ_zigzag(line, start_up=True):
    from feynplot.core.line import Line # 只在这里导入，避免在函数外层导入 Line，以防循环依赖

    if not isinstance(line, Line):
        raise TypeError("传入的 'line' 必须是 Line (或其子类，如 WPlusLine, ZBosonLine) 的实例。")
    
    if line.v_start is None or line.v_end is None:
        raise ValueError("Line 的起点和终点顶点必须在生成路径前设置。")

    start_point_coords = (line.v_start.x, line.v_start.y)
    end_point_coords = (line.v_end.x, line.v_end.y)
    angle_out = line.angleOut
    angle_in = line.angleIn
    bezier_offset = getattr(line, 'bezier_offset', 0.0) 
    
    zigzag_amplitude = getattr(line, 'zigzag_amplitude', 0.2)
    zigzag_frequency = getattr(line, 'zigzag_frequency', 2.0)
    points_per_cycle = getattr(line, 'zigzag_points_per_cycle', 4)

    # 定义贝塞尔曲线的采样点数 (现在这个点数将用于所有相关计算)
    num_bezier_points = 2000 
    
    A = np.array(start_point_coords)
    B = np.array(end_point_coords)

    # **一次性生成贝塞尔曲线路径 (使用定义的 num_bezier_points)**
    xs_bezier, ys_bezier = cubic_bezier(A, B, angle_out, angle_in, offset_ratio=bezier_offset, points=num_bezier_points)
    
    # 高分辨率贝塞尔路径就是这个结果
    high_res_bezier_path = np.column_stack((xs_bezier, ys_bezier))
    
    # 用于对齐的贝塞尔路径也是这个结果（因为点数相同）
    bezier_base_path_for_zigzag = high_res_bezier_path 

    # 计算切线向量和法线向量 (基于这次计算出的贝塞尔路径)
    t_vals = np.linspace(0, 1, num_bezier_points)
    # 再次强调：如果 bezier_tangent 需要 offset_ratio，这里也应该传入
    dxdt, dydt = bezier_tangent(A, B, angle_out, angle_in, t_vals,  offset_ratio=bezier_offset,) 
    
    tangent_len = np.sqrt(dxdt**2 + dydt**2)
    tangent_len[tangent_len == 0] = 1e-10 
    
    nx = dydt / tangent_len
    ny = -dxdt / tangent_len
    
    # 计算沿曲线的近似弧长 (基于这次计算出的贝塞尔路径)
    dx_segments = np.diff(xs_bezier) 
    dy_segments = np.diff(ys_bezier) 
    seg_len = np.sqrt(dx_segments**2 + dy_segments**2)
    arc_len = np.concatenate(([0], np.cumsum(seg_len)))
    
    total_arc_length = arc_len[-1]

    # 计算锯齿位移
    zigzag_displacement = np.zeros(num_bezier_points) # 锯齿位移数组大小与贝塞尔点数一致
    
    actual_zigzag_wavelength = 1.0 / zigzag_frequency if zigzag_frequency > 0 else total_arc_length

    for i in range(num_bezier_points): # 循环次数与贝塞尔点数一致
        zigzag_displacement[i] = find_zigzag_y(zigzag_amplitude, actual_zigzag_wavelength, arc_len[i], start_up)

    # 锯齿线坐标 = 曲线坐标 + 法线方向 * 锯齿位移
    xs_zigzag_path = xs_bezier + nx * zigzag_displacement
    ys_zigzag_path = ys_bezier + ny * zigzag_displacement
    zigzag_path = np.column_stack((xs_zigzag_path, ys_zigzag_path))
    
    # 返回锯齿路径、用于对齐的贝塞尔路径（现在和高分辨率路径是同一个对象）和高分辨率贝塞尔路径
    return zigzag_path, bezier_base_path_for_zigzag, high_res_bezier_path

# find_zigzag_y 函数保持不变
def find_zigzag_y(amplitude: float, wavelength: float, x: float, start_up: bool = True) -> float:
    """
    计算在给定 x 坐标处（沿直线路径的距离或相位）的锯齿波形 Y 偏移值。
    该函数模拟一个周期性的三角波（锯齿波）。

    参数:
        amplitude: 锯齿波的最大幅度。
        wavelength: 一个完整锯齿周期的长度。
        x: 沿路径的当前位置。
        start_up: 如果为 True，波形从 0 向上开始；如果为 False，从 0 向下开始。

    返回:
        在 x 处的 Y 偏移值。
    """
    if amplitude == 0 or wavelength == 0:
        return 0.0

    current_phase = math.fmod(x / wavelength, 1.0)
    
    if start_up:
        if current_phase < 0.25:
            return amplitude * (current_phase * 4)
        elif current_phase < 0.5:
            return amplitude * (1 - (current_phase - 0.25) * 4)
        elif current_phase < 0.75:
            return -amplitude * ((current_phase - 0.5) * 4)
        else:
            return -amplitude * (1 - (current_phase - 0.75) * 4)
    else: # start_down
        if current_phase < 0.25:
            return -amplitude * (current_phase * 4)
        elif current_phase < 0.5:
            return -amplitude * (1 - (current_phase - 0.25) * 4)
        elif current_phase < 0.75:
            return amplitude * ((current_phase - 0.5) * 4)
        else:
            return amplitude * (1 - (current_phase - 0.75) * 4)