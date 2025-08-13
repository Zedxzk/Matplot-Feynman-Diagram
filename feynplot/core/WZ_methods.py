import numpy as np
import math

# 假设 cubic_bezier 和 bezier_tangent 定义在 feynplot.core.bezier 中
from feynplot.core.bezier import cubic_bezier, bezier_tangent
from feynplot.core.circle import oval_circle


def generate_WZ_zigzag(line):
    from feynplot.core.line import WMinusLine, WPlusLine, ZBosonLine

    if not isinstance(line, (WMinusLine, WPlusLine, ZBosonLine)):
        raise TypeError("传入的 'line' 必须是 WMinusLine, WPlusLine, ZBosonLine 的实例。")
    
    if line.v_start is None or line.v_end is None:
        raise ValueError("Line 的起点和终点顶点必须在生成路径前设置。")

    start_point_coords = (line.v_start.x, line.v_start.y)
    end_point_coords = (line.v_end.x, line.v_end.y)
    angle_out = getattr(line, 'angleOut', 0.0)
    angle_in = getattr(line, 'angleIn', 0.0)
    bezier_offset = getattr(line, 'bezier_offset', 0.0)
    
    zigzag_amplitude = getattr(line, 'zigzag_amplitude', 0.2)
    zigzag_frequency = getattr(line, 'zigzag_frequency', 2.0)
    
    num_bezier_points = 2000 
    
    A = np.array(start_point_coords)
    B = np.array(end_point_coords)

    # --- 生成基础路径 ---
    if getattr(line, 'loop', False):
        results = oval_circle(
            start_point_coords, 
            getattr(line, 'angular_direction', 0.0), 
            getattr(line, 'a', 1.0), 
            getattr(line, 'b', 0.5), 
            points=num_bezier_points
        )
        xs, ys = results[:, 0], results[:, 1]
    else:
        xs, ys = cubic_bezier(A, B, angle_out, angle_in, offset_ratio=bezier_offset, points=num_bezier_points)
    
    base_path = np.column_stack((xs, ys))


    # --- 使用相邻点计算切线和法线 ---
    # dx, dy 是相邻两点的差值，即切线向量
    dxdt = np.diff(xs)
    dydt = np.diff(ys)
    
    # 数组的长度会减1，为了保持长度一致，可以对最后一个点使用前一个点的切线
    dxdt = np.append(dxdt, dxdt[-1])
    dydt = np.append(dydt, dydt[-1])

    # 计算法线向量
    tangent_len = np.sqrt(dxdt**2 + dydt**2)
    tangent_len[tangent_len == 0] = 1e-10 
    
    nx = dydt / tangent_len
    ny = -dxdt / tangent_len
    
    # 计算弧长
    seg_len = np.sqrt(np.diff(xs)**2 + np.diff(ys)**2)
    arc_len = np.concatenate(([0], np.cumsum(seg_len)))
    total_arc_length = arc_len[-1]

    # ---- 自动微调频率以匹配自然闭合 ----
    raw_n_cycles = getattr(line, 'zigzag_frequency', 2.0) * total_arc_length
    n_half_cycles = round(raw_n_cycles * 2) 
    if line.initial_phase == 0:
        n_half_cycles += 1
    if line.final_phase == 0:
        n_half_cycles += 1
    
    if total_arc_length > 1e-6:
        adjusted_frequency = (n_half_cycles / 2.0) / total_arc_length
    else:
        adjusted_frequency = 0.0

    actual_zigzag_wavelength = 1.0 / adjusted_frequency if adjusted_frequency > 0 else total_arc_length
    # ------------------------------------
    
    # 计算锯齿位移
    start_up = (getattr(line, 'initial_phase', 0) == 0)
    zigzag_displacement = np.zeros(num_bezier_points)
    for i in range(num_bezier_points):
        zigzag_displacement[i] = find_zigzag_y(zigzag_amplitude, actual_zigzag_wavelength, arc_len[i], start_up)

    # 生成锯齿线
    xs_zigzag_path = xs + nx * zigzag_displacement
    ys_zigzag_path = ys + ny * zigzag_displacement
    zigzag_path = np.column_stack((xs_zigzag_path, ys_zigzag_path))
    
    return zigzag_path, base_path


# find_zigzag_y 函数保持不变
def find_zigzag_y(amplitude: float, wavelength: float, x: float, start_up: bool = True) -> float:
    #... (保持不变)
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