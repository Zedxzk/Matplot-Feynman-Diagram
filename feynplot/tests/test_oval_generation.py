import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

def generate_ellipse_loop(
    center: Tuple[float, float], 
    radius: float, 
    start_angle: float, 
    end_angle: float,
    rotation_deg: float,
    points: int = 200
) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成一个用于费曼图自环的椭圆弧。
    
    参数:
        center: 椭圆的中心点坐标 (x, y)。
        radius: 椭圆的半径。
        start_angle: 椭圆弧的起始角度 (以度为单位)。
        end_angle: 椭圆弧的结束角度 (以度为单位)。
        rotation_deg: 椭圆相对于水平方向的旋转角度 (以度为单位)。
        points: 曲线上的采样点数。

    返回:
        xs, ys: 椭圆弧的 x 和 y 坐标数组。
    """
    # 将角度转换为弧度
    start_rad = np.deg2rad(start_angle)
    end_rad = np.deg2rad(end_angle)
    rotation_rad = np.deg2rad(rotation_deg)

    # 在指定角度范围内生成参数 t
    t = np.linspace(start_rad, end_rad, points)

    # 生成未旋转的圆形坐标
    x_circle = radius * np.cos(t)
    y_circle = radius * np.sin(t)

    # 应用旋转变换
    rot_matrix = np.array([
        [np.cos(rotation_rad), -np.sin(rotation_rad)],
        [np.sin(rotation_rad),  np.cos(rotation_rad)]
    ])
    rotated_coords = np.dot(rot_matrix, np.vstack((x_circle, y_circle)))

    # 应用中心点偏移
    xs = rotated_coords[0, :] + center[0]
    ys = rotated_coords[1, :] + center[1]

    return xs, ys


# 1. 定义顶点
v1 = (0, 0)
v2 = (5, 0)

# 2. 定义自环的参数
loop_center = (2.5, 1.5)  # 自环的中心
loop_radius = 1.0         # 自环的半径
loop_rotation = 0         # 旋转角度，例如45度会倾斜
loop_start_angle = 0      # 从0度开始
loop_end_angle = 360      # 到360度结束，形成一个完整的圆

# 3. 定义外部线条
line_xs = [v1[0], v2[0]]
line_ys = [v1[1], v2[1]]

# 4. 生成自环的坐标
loop_xs, loop_ys = generate_ellipse_loop(
    center=loop_center,
    radius=loop_radius,
    start_angle=loop_start_angle,
    end_angle=loop_end_angle,
    rotation_deg=loop_rotation
)

# 5. 使用 Matplotlib 绘图
fig, ax = plt.subplots(figsize=(8, 6))

# 绘制自环
ax.plot(loop_xs, loop_ys, color='blue', linewidth=2, linestyle='-')
# 绘制外部线条
ax.plot(line_xs, line_ys, color='black', linewidth=2, linestyle='-')

# 在顶点位置绘制点
ax.plot(v1[0], v1[1], 'o', markersize=8, color='red')
ax.plot(v2[0], v2[1], 'o', markersize=8, color='red')
ax.set_aspect('equal', adjustable='box')
ax.set_title("Feynman Diagram with a Self-loop")
ax.grid(True)
plt.show()