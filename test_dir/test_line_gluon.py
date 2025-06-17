import numpy as np
import matplotlib.pyplot as plt
import feynplot.core.bezire as bezire

def find_closest_intersection_point(central_point, radius, path):
    """
    找路径中距离圆最近（即最接近圆周）的一个点。
    返回 (index, vector)：索引和交点相对中心点的向量
    """
    path = np.array(path)
    center = np.array(central_point)
    distances = np.linalg.norm(path - center, axis=1)
    diff = np.abs(distances - radius)

    idx = np.argmin(diff)
    vec = - path[idx] + center  # 向量从路径点指向中心点
    return idx, vec

def compute_path_length(path):
    """
    计算路径的总长度。
    """
    diffs = np.diff(path, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    return np.sum(segment_lengths)

def cubic_bezier(t, P0, P1, P2, P3):
    """Cubic Bezier curve definition"""
    return (1 - t)**3 * P0 + 3 * (1 - t)**2 * t * P1 + 3 * (1 - t) * t**2 * P2 + t**3 * P3

# ----------------------- 参数设置 -----------------------

# 控制点定义
P0 = np.array([0, 0])      # A
P1 = np.array([1, 2])      # 控制点1
P2 = np.array([4, 2])     # 控制点2
P3 = np.array([5, 0])      # B

A = P0
B = P3
radius = 0.3  # 圆半径（用于 D 绕 C 转动，及交点判断）

# 生成贝塞尔路径
t_vals = np.linspace(0, 1, 1000)
# path = np.array([bezire.cubic_bezier(t, A, B, 20, 160) for t in t_vals])
# xs, ys = bezire.cubic_bezier(A, B, 45, 135)
path = bezire.generate_bezier_path(A, B, 45, 135)
# ----------------------- 截取路径段 -----------------------

idx_A, vec_A = find_closest_intersection_point(A, radius, path)
idx_B, vec_B = find_closest_intersection_point(B, radius, path)

start_idx = min(idx_A, idx_B)
end_idx = max(idx_A, idx_B)
truncated_path = path[start_idx:end_idx+1]

vec_A_to_path_point = vec_A
vec_B_to_path_point = vec_B

initial_phase_angle = np.arctan2(vec_A_to_path_point[1], vec_A_to_path_point[0])
final_phase_angle = np.arctan2(vec_B_to_path_point[1], vec_B_to_path_point[0])

truncated_path_length = compute_path_length(truncated_path)
total_phase_from_path_calc = 2 * np.pi * 10 + final_phase_angle - initial_phase_angle

# ----------------------- D 点运动模拟 -----------------------

v = 2  # C 沿路径的速度
total_time = truncated_path_length / v
omega = total_phase_from_path_calc / total_time  # D 绕 C 的角速度

num_steps = len(truncated_path)
dt = total_time / (num_steps - 1) if num_steps > 1 else 0

D_trajectory = np.zeros_like(truncated_path)

for i, point_C in enumerate(truncated_path):
    current_time = i * dt
    current_phase_D_rel_C = initial_phase_angle + omega * current_time

    dx = radius * np.cos(current_phase_D_rel_C)
    dy = radius * np.sin(current_phase_D_rel_C)

    D_trajectory[i, 0] = point_C[0] + dx
    D_trajectory[i, 1] = point_C[1] + dy

# ----------------------- 输出信息 -----------------------

print(f"Truncated path length: {truncated_path_length:.4f}")
print(f"Initial phase angle:   {initial_phase_angle:.4f} rad")
print(f"Final phase angle:     {final_phase_angle:.4f} rad")
print(f"Total phase:           {total_phase_from_path_calc:.4f} rad")
print(f"Total simulation time: {total_time:.4f}")
print(f"Angular velocity ω:    {omega:.4f} rad/time")

# ----------------------- 绘图 -----------------------

fig, ax = plt.subplots(figsize=(10, 8))

ax.plot(path[:, 0], path[:, 1], color='gray', linestyle='--', label='Full Bezier Path')
ax.plot(truncated_path[:, 0], truncated_path[:, 1], color='red', linewidth=2, label='Truncated Path (C\'s Path)')

# 起点和终点
ax.scatter(*A, color='blue', label='Point A')
ax.scatter(*B, color='green', label='Point B')

# 圆圈
circle_A = plt.Circle(A, radius, color='blue', fill=False, linestyle=':', label='Start Circle')
circle_B = plt.Circle(B, radius, color='green', fill=False, linestyle=':', label='End Circle')
ax.add_patch(circle_A)
ax.add_patch(circle_B)

# 交点
intersection_A = path[idx_A]
intersection_B = path[idx_B]
ax.scatter(*intersection_A, color='blue', s=50, label='Start Intersection')
ax.scatter(*intersection_B, color='green', s=50, label='End Intersection')

# C 点起止
ax.scatter(truncated_path[0, 0], truncated_path[0, 1], color='purple', marker='o', s=80, zorder=5, label='C Start')
ax.scatter(truncated_path[-1, 0], truncated_path[-1, 1], color='brown', marker='o', s=80, zorder=5, label='C End')

# D 点轨迹
ax.plot(D_trajectory[:, 0], D_trajectory[:, 1], color='darkorange', linewidth=1.5, label='D\'s Trajectory')
ax.scatter(D_trajectory[0, 0], D_trajectory[0, 1], color='darkorange', marker='s', s=80, zorder=5, label='D Start')
ax.scatter(D_trajectory[-1, 0], D_trajectory[-1, 1], color='darkorange', marker='X', s=80, zorder=5, label='D End')

# 向量箭头
ax.arrow(A[0], A[1], vec_A_to_path_point[0], vec_A_to_path_point[1], head_width=0.1, head_length=0.1, fc='blue', ec='blue', alpha=0.5)
ax.arrow(B[0], B[1], vec_B_to_path_point[0], vec_B_to_path_point[1], head_width=0.1, head_length=0.1, fc='green', ec='green', alpha=0.5)

ax.set_aspect('equal')
ax.set_title("Bezier Path & Rotating Point D Trajectory")
ax.grid(True)
ax.legend()
plt.tight_layout()
plt.show()
