import numpy as np

def cubic_bezier(A, B, angleA_deg, angleB_deg, offset_ratio=0.3, points=2000):
    """
    生成从点 A 到点 B 的三次贝塞尔曲线。
    
    参数:
        A, B: 起点和终点坐标，格式为 [x, y]。
        angleA_deg: 起点切线角度（以度为单位，逆时针方向，0 度表示向右）。
        angleB_deg: 终点切线角度（以度为单位）。
        offset_ratio: 控制点相对于 AB 直线长度的偏移比例。
        points: 曲线上采样的点数。

    返回:
        xs, ys: 曲线的 x 和 y 坐标数组。
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)

    dist = np.linalg.norm(B - A)

    angleA_rad = np.deg2rad(angleA_deg)
    angleB_rad = np.deg2rad(angleB_deg)

    C1 = A + offset_ratio * dist * np.array([np.cos(angleA_rad), np.sin(angleA_rad)])
    C2 = B + offset_ratio * dist * np.array([np.cos(angleB_rad), np.sin(angleB_rad)])

    t = np.linspace(0, 1, points)
    xs = (1 - t)**3 * A[0] + 3*(1 - t)**2 * t * C1[0] + 3*(1 - t)*t**2 * C2[0] + t**3 * B[0]
    ys = (1 - t)**3 * A[1] + 3*(1 - t)**2 * t * C1[1] + 3*(1 - t)*t**2 * C2[1] + t**3 * B[1]

    return xs, ys


def generate_bezier_path(A, B, angleA_deg, angleB_deg, offset_ratio=0.3, points=2000):
    """
    封装函数，返回贝塞尔路径的二维坐标点组成的 (N, 2) 数组。
    """
    xs, ys = cubic_bezier(A, B, angleA_deg, angleB_deg, offset_ratio, points)
    return np.column_stack((xs, ys))
