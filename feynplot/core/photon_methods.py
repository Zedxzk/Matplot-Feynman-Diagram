import numpy as np
import math
from feynplot.core.circle import oval_circle
from feynplot.core.bezier import cubic_bezier, bezier_tangent
from feynplot.core.line import Line, PhotonLine

def generate_photon_wave(line, loop=False):
    """
    根据 PhotonLine 实例生成光子波浪线的路径点，
    并确保波浪线在起点和终点处与指定相位对齐。
    
    参数:
        line: 一个 PhotonLine 实例，必须已设置 v_start, v_end, angleOut, angleIn, 
              以及可选的 amplitude, wavelength, initial_phase, final_phase 属性。
        loop: 布尔值，指示是否生成环形路径。
              如果为 True，将使用 oval_circle 生成环形路径。
              
    返回:
        一个 NumPy 数组 (N, 2)，包含光子波浪线的 (x, y) 坐标点序列。
        
    异常:
        TypeError: 如果传入的 'line' 不是 Line 实例。
        ValueError: 如果 'line' 的起点或终点未设置。
    """
    if not isinstance(line, Line): 
        raise TypeError("传入的 'line' 必须是 Line (或其子类，如 PhotonLine) 的实例。")
    
    if line.v_start is None or line.v_end is None:
        raise ValueError("Line 的起点和终点顶点必须在生成路径前设置。")

    start_point_coords = (line.v_start.x, line.v_start.y)
    end_point_coords = (line.v_end.x, line.v_end.y)
    
    amplitude = getattr(line, 'amplitude', 0.1) 
    nominal_wavelength = getattr(line, 'wavelength', 0.5) 
    initial_phase_deg = getattr(line, 'initial_phase', 0)
    final_phase_deg = getattr(line, 'final_phase', 0)

    initial_phase_rad = np.deg2rad(initial_phase_deg)
    final_phase_rad = np.deg2rad(final_phase_deg)

    points = 2000
    
    # --- 完善 loop 和 not loop 两种情况的路径生成 ---
    if not loop:
        # 非环形路径：使用贝塞尔曲线
        angle_out = line.angleOut
        angle_in = line.angleIn
        bezier_offset = getattr(line, 'bezier_offset', 0.0)
        
        A = np.array(start_point_coords)
        B = np.array(end_point_coords)

        xs_bezier, ys_bezier = cubic_bezier(A, B, angle_out, angle_in, points=points, offset_ratio=bezier_offset)
        bezier_coords = np.column_stack((xs_bezier, ys_bezier))

        # 计算贝塞尔曲线的切线向量 (dx/dt, dy/dt)
        t = np.linspace(0, 1, points)
        dxdt, dydt = bezier_tangent(A, B, angle_out, angle_in, t, offset_ratio=bezier_offset)
        
    else:
        # 环形路径：使用 oval_circle
        try:
            bezier_coords = oval_circle(
                start_point=start_point_coords,
                angular_direction=line.angular_direction,
                a=line.a,
                b=line.b,
                points=points
            )
            
        except ValueError as e:
            raise ValueError(f"生成环形路径失败: {e}")

        # 对于非贝塞尔曲线，通过前后点差值来近似切线
        # dxdt 和 dydt 的长度比 bezier_coords 短 1
        dxdt = np.diff(bezier_coords[:, 0], prepend=bezier_coords[0, 0])
        dydt = np.diff(bezier_coords[:, 1], prepend=bezier_coords[0, 1])

    # --- 后续计算波浪的通用部分 ---

    # 计算切线长度，并避免除以零
    tangent_len = np.sqrt(dxdt**2 + dydt**2)
    tangent_len[tangent_len == 0] = 1e-10 
    
    # 计算法线方向（垂直于切线）的单位向量：顺时针旋转90度
    nx = dydt / tangent_len
    ny = -dxdt / tangent_len
    
    # 计算沿曲线的近似弧长
    dx_segments = np.diff(bezier_coords[:, 0], prepend=bezier_coords[0, 0])
    dy_segments = np.diff(bezier_coords[:, 1], prepend=bezier_coords[0, 1])
    seg_len = np.sqrt(dx_segments**2 + dy_segments**2)
    arc_len = np.cumsum(seg_len)
    
    total_arc_length = arc_len[-1]

    # 根据初始和最终相位调整波长
    if nominal_wavelength <= 0 or total_arc_length == 0:
        wave_displacement = np.zeros(points)
    else:
        phase_difference_rad = (final_phase_rad - initial_phase_rad) % (2 * np.pi)
        if abs(phase_difference_rad) < 1e-9 or abs(phase_difference_rad - 2 * np.pi) < 1e-9:
            target_half_cycles = round(total_arc_length * 2 / nominal_wavelength / 2.0) * 2.0 
        else:
            target_half_cycles = round((total_arc_length * 2 / nominal_wavelength - 1) / 2.0) * 2.0 + 1.0
            
        if target_half_cycles < 0.5:
            target_half_cycles = 0.5

        effective_wavelength = total_arc_length / (target_half_cycles / 2.0)
        
        # 计算波浪位移
        wave_displacement = amplitude * np.sin(2 * np.pi * arc_len / effective_wavelength + initial_phase_rad)
    
    # 波浪线坐标 = 曲线坐标 + 法线方向 * 波浪位移
    xs_wave = bezier_coords[:, 0] + nx * wave_displacement
    ys_wave = bezier_coords[:, 1] + ny * wave_displacement
    
    return np.column_stack((xs_wave, ys_wave))