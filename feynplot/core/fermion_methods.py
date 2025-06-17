import numpy as np
import math

# 假设 cubic_bezier 定义在 feynplot.core.bezier 中
from feynplot.core.bezier import cubic_bezier

def generate_fermion_line(line):
    """
    根据 FermionLine 实例生成费米子线的平滑贝塞尔曲线路径点。
    
    参数:
        line: 一个 FermionLine 实例，必须已设置 v_start, v_end, angleOut, angleIn。
              Line 实例应包含以下用于贝塞尔曲线的属性（或默认值）：
              - bezier_offset: 控制点相对于起点-终点直线长度的偏移比例。
    
    返回:
        一个 NumPy 数组 (N, 2)，包含费米子线的 (x, y) 坐标点序列。
        
    异常:
        TypeError: 如果传入的 'line' 不是 Line 实例。
        ValueError: 如果起点或终点未设置。
    """
    # 在函数内部导入 Line，以避免循环依赖问题
    # 假设 FermionLine 是 Line 的子类，并且定义在 feynplot.core.line 中
    from feynplot.core.line import Line, FermionLine # 确保导入 FermionLine

    if not isinstance(line, Line):
        raise TypeError("传入的 'line' 必须是 Line (或其子类，如 FermionLine) 的实例。")
    
    if line.v_start is None or line.v_end is None:
        raise ValueError("Line 的起点和终点顶点必须在生成路径前设置。")

    start_point_coords = (line.v_start.x, line.v_start.y)
    end_point_coords = (line.v_end.x, line.v_end.y)
    angle_out = line.angleOut
    angle_in = line.angleIn
    bezier_offset = getattr(line, 'bezier_offset', 0.0) # 获取 bezier_offset，默认为0.0
    
    # 费米子线只需要高分辨率的平滑曲线，所以我们直接定义点数
    num_points = 2000 # 可以根据需要调整平滑度
    
    A = np.array(start_point_coords)
    B = np.array(end_point_coords)

    # 直接生成贝塞尔曲线路径
    xs, ys = cubic_bezier(A, B, angle_out, angle_in, offset_ratio=bezier_offset, points=num_points)
    
    # 返回 (N, 2) 形状的路径数组
    return np.column_stack((xs, ys))