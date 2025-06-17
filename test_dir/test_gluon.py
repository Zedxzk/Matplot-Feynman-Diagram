import numpy as np
import matplotlib.pyplot as plt

def gluon_line(A, B, amplitude=0.2, wavelength=0.5, points=5000):
    A = np.array(A)
    B = np.array(B)
    vec = B - A
    length = np.linalg.norm(vec)
    direction = vec / length
    normal = np.array([-direction[1], direction[0]])
    t = np.linspace(0, length, points)
    wave = amplitude * np.sin(2 * np.pi * t / wavelength)
    xs = A[0] + direction[0] * t + normal[0] * wave
    ys = A[1] + direction[1] * t + normal[1] * wave
    return xs, ys

def cubic_bezier(A, B, angleA_deg, angleB_deg, offset_ratio=0.3, points=2000):
    A = np.array(A)
    B = np.array(B)
    dist = np.linalg.norm(B - A)
    angleA_rad = np.deg2rad(angleA_deg)
    C1 = A + offset_ratio * dist * np.array([np.cos(angleA_rad), np.sin(angleA_rad)])
    angleB_rad = np.deg2rad(angleB_deg)
    C2 = B + offset_ratio * dist * np.array([np.cos(angleB_rad), np.sin(angleB_rad)])
    t = np.linspace(0, 1, points)
    xs = (1 - t)**3 * A[0] + 3*(1 - t)**2 * t * C1[0] + 3*(1 - t)*t**2 * C2[0] + t**3 * B[0]
    ys = (1 - t)**3 * A[1] + 3*(1 - t)**2 * t * C1[1] + 3*(1 - t)*t**2 * C2[1] + t**3 * B[1]
    return xs, ys

def bezier_tangent(A, B, angleA_deg, angleB_deg, t_vals):
    """
    计算三次贝塞尔曲线在参数t处的切线向量（dx/dt, dy/dt）
    """
    A = np.array(A)
    B = np.array(B)
    dist = np.linalg.norm(B - A)
    angleA_rad = np.deg2rad(angleA_deg)
    C1 = A + 0.3 * dist * np.array([np.cos(angleA_rad), np.sin(angleA_rad)])
    angleB_rad = np.deg2rad(angleB_deg)
    C2 = B + 0.3 * dist * np.array([np.cos(angleB_rad), np.sin(angleB_rad)])
    
    t = t_vals
    dxdt = 3*(1 - t)**2 * (C1[0] - A[0]) + 6*(1 - t)*t * (C2[0] - C1[0]) + 3*t**2 * (B[0] - C2[0])
    dydt = 3*(1 - t)**2 * (C1[1] - A[1]) + 6*(1 - t)*t * (C2[1] - C1[1]) + 3*t**2 * (B[1] - C2[1])
    return dxdt, dydt

def gluon_on_bezier(A, B, angleA_deg, angleB_deg, amplitude=0.1, wavelength=0.1, points=2000):
    # 计算贝塞尔曲线点
    xs, ys = cubic_bezier(A, B, angleA_deg, angleB_deg, points=points)
    
    # 参数 t 从0到1
    t = np.linspace(0, 1, points)
    
    # 计算切线向量
    dxdt, dydt = bezier_tangent(A, B, angleA_deg, angleB_deg, t)
    
    # 计算切线长度，防止除0
    tangent_len = np.sqrt(dxdt**2 + dydt**2)
    tangent_len[tangent_len == 0] = 1e-10
    
    # 计算法线方向（垂直切线）单位向量：顺时针旋转90度
    nx = dydt / tangent_len
    ny = -dxdt / tangent_len
    
    # 按参数t计算沿曲线的弧长近似，做波浪函数参数（避免t均匀时波浪波长不均匀）
    # 简单用t * 总长度近似波长
    # 先计算点间距离
    dx = np.diff(xs)
    dy = np.diff(ys)
    seg_len = np.sqrt(dx**2 + dy**2)
    arc_len = np.concatenate(([0], np.cumsum(seg_len)))
    
    # 计算波浪位移
    wave = amplitude * np.sin(2 * np.pi * arc_len / wavelength)
    
    # 波浪线坐标 = 曲线坐标 + 法线方向 * 波浪位移
    xs_wave = xs + nx * wave
    ys_wave = ys + ny * wave
    
    return xs_wave, ys_wave

# 示例点和角度
A = (1, 1)
B = (5, 4)
angleA = 60
angleB = 120

xs_curve, ys_curve = cubic_bezier(A, B, angleA, angleB)
xs_wave, ys_wave = gluon_on_bezier(A, B, angleA, angleB, amplitude=0.15, wavelength=0.3)

plt.figure(figsize=(7,7))
plt.plot(xs_curve, ys_curve, label="Smooth cubic Bezier curve", zorder=100)
plt.plot(xs_wave, ys_wave, label="Wave on Bezier curve", zorder=100)
plt.scatter(*A, color='red', label="Point A", zorder=10)
plt.scatter(*B, color='green', label="Point B", zorder=10)
plt.axis('equal')
plt.legend()
plt.title("Wave line perpendicular to cubic Bezier curve")
plt.show()
