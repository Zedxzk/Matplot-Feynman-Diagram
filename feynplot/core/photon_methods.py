import numpy as np
import math

from regex import P

# 确保导入你的 Bezier 曲线函数
from feynplot.core.bezier import cubic_bezier, bezier_tangent

def generate_photon_wave(line):
    """
    根据 PhotonLine 实例生成光子波浪线的路径点，
    并确保波浪线在起点和终点处与指定相位对齐。
    
    参数:
        line: 一个 PhotonLine 实例，必须已设置 v_start, v_end, angleOut, angleIn, 
              以及可选的 amplitude, wavelength, initial_phase, final_phase 属性。
              
    返回:
        一个 NumPy 数组 (N, 2)，包含光子波浪线的 (x, y) 坐标点序列。
        
    异常:
        TypeError: 如果传入的 'line' 不是 Line 实例。
        ValueError: 如果 'line' 的起点或终点未设置。
    """
    from feynplot.core.line import Line, PhotonLine

    if not isinstance(line, Line): 
        raise TypeError("传入的 'line' 必须是 Line (或其子类，如 PhotonLine) 的实例。")
    
    if line.v_start is None or line.v_end is None:
        raise ValueError("Line 的起点和终点顶点必须在生成路径前设置。")

    start_point_coords = (line.v_start.x, line.v_start.y)
    end_point_coords = (line.v_end.x, line.v_end.y)
    angle_out = line.angleOut
    angle_in = line.angleIn
    bezier_offset = getattr(line, 'bezier_offset', 0.0)
    
    amplitude = getattr(line, 'amplitude', 0.1) 
    nominal_wavelength = getattr(line, 'wavelength', 0.5) 
    
    # 获取新的相位参数，确保它们存在
    initial_phase_deg = getattr(line, 'initial_phase', 0)
    final_phase_deg = getattr(line, 'final_phase', 0)

    # 将度数转换为弧度，用于 np.sin 的初始偏移
    initial_phase_rad = np.deg2rad(initial_phase_deg)
    final_phase_rad = np.deg2rad(final_phase_deg)

    # 定义生成贝塞尔曲线点的数量
    points = 2000 
    
    A = np.array(start_point_coords)
    B = np.array(end_point_coords)

    # 计算贝塞尔曲线点
    xs_bezier, ys_bezier = cubic_bezier(A, B, angle_out, angle_in, points=points, offset_ratio=bezier_offset)
    
    # 参数 t 从0到1，用于计算切线
    t = np.linspace(0, 1, points)
    
    # 计算切线向量 (dx/dt, dy/dt)
    dxdt, dydt = bezier_tangent(A, B, angle_out, angle_in, t, offset_ratio=bezier_offset)
    
    # 计算切线长度，并避免除以零
    tangent_len = np.sqrt(dxdt**2 + dydt**2)
    tangent_len[tangent_len == 0] = 1e-10 
    
    # 计算法线方向（垂直于切线）的单位向量：顺时针旋转90度
    nx = dydt / tangent_len
    ny = -dxdt / tangent_len
    
    # 计算沿曲线的近似弧长
    dx_segments = np.diff(xs_bezier)
    dy_segments = np.diff(ys_bezier)
    seg_len = np.sqrt(dx_segments**2 + dy_segments**2)
    arc_len = np.concatenate(([0], np.cumsum(seg_len)))
    
    total_arc_length = arc_len[-1]

    # --- 关键修改：根据初始和最终相位调整波长 ---
    if nominal_wavelength <= 0 or total_arc_length == 0:
        wave_displacement = np.zeros(points)
    else:
        # 计算总相移差 (0 或 pi)
        phase_difference_rad = (final_phase_rad - initial_phase_rad) % (2 * np.pi)
        
        # 目标是让 (2 * np.pi * total_arc_length / effective_wavelength + initial_phase_rad) 
        # 等于 final_phase_rad + N * 2 * np.pi 
        # 简化后，我们关注弧长需要满足的条件：
        # total_arc_length / effective_wavelength 应该使最终相位与 initial_phase_rad 的差为 phase_difference_rad
        # 这意味着 (total_arc_length / effective_wavelength) * 2 * np.pi 应该等于 phase_difference_rad + K * 2 * np.pi
        # total_arc_length / effective_wavelength 应该等于 (phase_difference_rad / (2 * np.pi)) + K
        
        # 计算基于标称波长的理想半周期数
        # 理想情况下，从 0 到 0 需 N 个全波（2N 个半波），从 0 到 180 需 N.5 个全波（2N+1 个半波）
        # 这里，我们用 'effective_distance_for_waves' 来表示波浪需要覆盖的“有效”距离
        
        # 计算标称波长下的完整周期数
        num_full_cycles_float = total_arc_length / nominal_wavelength

        # 计算最接近的，满足相位要求的半周期数
        if abs(phase_difference_rad) < 1e-9: # 初始相位和最终相位相同 (0 到 0, 180 到 180)
            # 需要偶数个半周期 (N个完整周期)
            target_half_cycles = round(num_full_cycles_float * 2 / 2.0) * 2.0 
        else: # 初始相位和最终相位不同 (0 到 180, 180 到 0)
            # 需要奇数个半周期 (N.5个完整周期)
            target_half_cycles = round((num_full_cycles_float * 2 - 1) / 2.0) * 2.0 + 1.0
            
        # 确保至少有 0.5 个半周期（至少一个波峰或波谷）
        if target_half_cycles < 0.5:
            target_half_cycles = 0.5

        # 计算实际使用的波长
        effective_wavelength = total_arc_length / (target_half_cycles / 2.0) # target_half_cycles / 2.0 才是完整周期数
        
        # 计算波浪位移
        # 注意：现在我们在 sin 函数中加入了 initial_phase_rad 作为偏移
        # from pprint import pprint
        # pprint(arc_len[:10])
        wave_displacement = amplitude * np.sin(2 * np.pi * arc_len / effective_wavelength + initial_phase_rad)
    
    # 波浪线坐标 = 曲线坐标 + 法线方向 * 波浪位移
    xs_wave = xs_bezier + nx * wave_displacement
    ys_wave = ys_bezier + ny * wave_displacement
    
    return np.column_stack((xs_wave, ys_wave))