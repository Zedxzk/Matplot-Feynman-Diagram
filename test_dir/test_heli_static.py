import numpy as np
import matplotlib.pyplot as plt

def bezier_curve(P0, P1, P2, P3, t):
    return (1-t)**3 * P0 + 3*(1-t)**2 * t * P1 + 3*(1-t)*t**2 * P2 + t**3 * P3

def bezier_points(P0, P1, P2, P3, num=1000):
    ts = np.linspace(0,1,num)
    return np.array([bezier_curve(P0,P1,P2,P3,t) for t in ts]), ts

def find_circle_intersections(Ps, center, radius):
    dist = np.linalg.norm(Ps - center, axis=1)
    close_to_circle = np.abs(dist - radius) < 1e-3
    indices = np.where(close_to_circle)[0]
    return indices

def compute_tangents(points):
    """计算路径上每一点的切向量（单位向量），边界用前后差分补偿"""
    tangents = np.zeros_like(points)
    tangents[1:-1] = points[2:] - points[:-2]
    tangents[0] = points[1] - points[0]
    tangents[-1] = points[-1] - points[-2]
    norms = np.linalg.norm(tangents, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return tangents / norms

def gluon_wave_along_path(points, amplitude=0.1, wavelength=0.5, phase0=0):
    """
    沿路径points绘制波浪，波动垂直于路径切线方向
    amplitude: 振幅
    wavelength: 波长
    phase0: 初始相位
    返回扰动后点坐标数组
    """
    tangents = compute_tangents(points)
    normals = np.stack([-tangents[:,1], tangents[:,0]], axis=1)  # 垂直切线向量，逆时针90度
    
    # 计算路径上每点的累计弧长
    deltas = np.linalg.norm(points[1:] - points[:-1], axis=1)
    s = np.zeros(len(points))
    s[1:] = np.cumsum(deltas)
    
    # 波浪函数
    wave = amplitude * np.sin(2 * np.pi * s / wavelength + phase0)
    
    # 波浪叠加在路径点上
    waved_points = points + normals * wave[:, np.newaxis]
    return waved_points

# ------------ 主程序 ------------

P0 = np.array([0, 0])
P1 = np.array([2, 3])
P2 = np.array([4, -1])
P3 = np.array([6, 2])

num_samples = 10000
points, ts = bezier_points(P0,P1,P2,P3,num_samples)

A = P0
B = P3
R_A = 0.7
R_B = 0.6

idxs_A = find_circle_intersections(points, A, R_A)
idxs_B = find_circle_intersections(points, B, R_B)

if len(idxs_A)==0 or len(idxs_B)==0:
    raise RuntimeError("找不到路径与圆的交点，请调整参数或增加采样密度。")

start_idx = idxs_A[np.argmin(np.abs(idxs_A - 0))]
end_idx = idxs_B[np.argmin(np.abs(idxs_B - (num_samples-1)))]

if start_idx >= end_idx:
    raise RuntimeError("起点交点索引不应大于等于终点交点索引，请检查路径或圆参数。")

C_path = points[start_idx:end_idx+1]

# 计算起点摆动初相位phase0，基于起点连线A->C_path起点的方向角
vec_start = C_path[0] - A
phase0 = np.arctan2(vec_start[1], vec_start[0])

# 绘制摆线轨迹
waved_path = gluon_wave_along_path(C_path, amplitude=R_A, wavelength=1.0, phase0=phase0)

# 画图
plt.figure(figsize=(8,6))
plt.plot(points[:,0], points[:,1], 'k--', label='Full path')
plt.plot(C_path[:,0], C_path[:,1], 'r-', linewidth=2, label='C path segment')
plt.plot(waved_path[:,0], waved_path[:,1], 'b-', linewidth=2, label='Wave along path')

# 画圆
circleA = plt.Circle(A, R_A, color='b', fill=False, linestyle=':', label='Circle A')
circleB = plt.Circle(B, R_B, color='g', fill=False, linestyle=':', label='Circle B')
plt.gca().add_patch(circleA)
plt.gca().add_patch(circleB)

plt.scatter(points[idxs_A,0], points[idxs_A,1], color='b', s=10)
plt.scatter(points[idxs_B,0], points[idxs_B,1], color='g', s=10)

plt.scatter(A[0], A[1], color='b', marker='o', label='Point A')
plt.scatter(B[0], B[1], color='g', marker='o', label='Point B')

plt.axis('equal')
plt.legend()
plt.title('Wave (gluon-like) along clipped path segment')
plt.show()
