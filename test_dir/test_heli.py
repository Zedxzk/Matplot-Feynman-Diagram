import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 定义点A, B
A = np.array([0, 0])
B = np.array([5, 3])

# 质点C沿AB匀速运动速度
v = 1  # 单位：距离/秒

# 点D绕C旋转半径和角速度
R = 0.5
omega = 4 * np.pi  # 2圈/秒

# 计算方向向量和长度
vec = B - A
length = np.linalg.norm(vec)
direction = vec / length

# 动画参数
fps = 60
t_max = length / v  # C从A到B所需时间
frames = int(fps * t_max)

fig, ax = plt.subplots(figsize=(8,6))
ax.plot([A[0], B[0]], [A[1], B[1]], 'k--', label='Line AB')

pointC, = ax.plot([], [], 'ro', label='Point C (moving)')
pointD, = ax.plot([], [], 'bo', label='Point D (rotating around C)')
trajC, = ax.plot([], [], 'r-', alpha=0.5)
trajD, = ax.plot([], [], 'b-', alpha=0.5)

ax.legend()
ax.set_xlim(min(A[0], B[0]) - 1, max(A[0], B[0]) + 1)
ax.set_ylim(min(A[1], B[1]) - 1, max(A[1], B[1]) + 1)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Particle C linear + D circular rotation')

# 存储轨迹点
trajC_x, trajC_y = [], []
trajD_x, trajD_y = [], []

def init():
    pointC.set_data([], [])
    pointD.set_data([], [])
    trajC.set_data([], [])
    trajD.set_data([], [])
    return pointC, pointD, trajC, trajD

def update(frame):
    t = frame / fps
    # C点位置（匀速直线运动）
    dist = min(v * t, length)
    posC = A + dist * direction
    
    # D点绕C旋转位置
    angle = omega * t
    # 计算垂直方向单位向量（顺时针旋转90度）
    normal = np.array([-direction[1], direction[0]])
    posD = posC + R * np.array([np.cos(angle) * normal[0] - np.sin(angle) * direction[0],
                               np.cos(angle) * normal[1] - np.sin(angle) * direction[1]])
    
    # 记录轨迹
    trajC_x.append(posC[0])
    trajC_y.append(posC[1])
    trajD_x.append(posD[0])
    trajD_y.append(posD[1])
    
    # 更新绘图数据
    pointC.set_data(posC[0], posC[1])
    pointD.set_data(posD[0], posD[1])
    trajC.set_data(trajC_x, trajC_y)
    trajD.set_data(trajD_x, trajD_y)
    return pointC, pointD, trajC, trajD

ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True, interval=1000/fps)
plt.show()
