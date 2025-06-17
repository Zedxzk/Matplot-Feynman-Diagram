import numpy as np
import matplotlib.pyplot as plt

def calculate_bezier_curve(t_values, P0, P1, P2, P3):
    """
    计算三次贝塞尔曲线上指定参数 t 对应点的坐标。

    参数:
    t_values (numpy.ndarray): 一个包含参数 t 值的 NumPy 数组，范围通常在 [0, 1]。
    P0 (numpy.ndarray): 第一个控制点，形状为 (2,) 或 (3,) (x, y) 或 (x, y, z)。
    P1 (numpy.ndarray): 第二个控制点。
    P2 (numpy.ndarray): 第三个控制点。
    P3 (numpy.ndarray): 第四个控制点。

    返回:
    numpy.ndarray: 曲线上对应 t 值的点，形状为 (len(t_values), 2) 或 (len(t_values), 3)。
    """
    # 广播 t_values 以便与控制点进行元素级乘法
    # (1-t)**3 * P0 等价于 ((1-t)**3).reshape(-1, 1) * P0
    term0 = np.power(1 - t_values, 3)[:, np.newaxis] * P0
    term1 = 3 * np.power(1 - t_values, 2)[:, np.newaxis] * t_values[:, np.newaxis] * P1
    term2 = 3 * (1 - t_values)[:, np.newaxis] * np.power(t_values, 2)[:, np.newaxis] * P2
    term3 = np.power(t_values, 3)[:, np.newaxis] * P3

    # 将所有项相加，得到曲线上每个 t 值的点
    curve_points = term0 + term1 + term2 + term3
    return curve_points

# 定义控制点 (P0, P1, P2, P3)
# 可以是二维或三维点
P0 = np.array([0, 0])
P1 = np.array([1, 2])
P2 = np.array([3, -1])
P3 = np.array([4, 1])

# 生成一系列 t 值，用于计算曲线上的点
t_values = np.linspace(0, 1, 100) # 生成100个从0到1的等间距t值

# 计算贝塞尔曲线上的点
bezier_points = calculate_bezier_curve(t_values, P0, P1, P2, P3)

# 绘制贝塞尔曲线和控制点
plt.figure(figsize=(8, 6))
plt.plot(bezier_points[:, 0], bezier_points[:, 1], label='Bezier Curve', color='blue')
plt.plot([P0[0], P1[0], P2[0], P3[0]],
         [P0[1], P1[1], P2[1], P3[1]], 'ro--', label='Control Points') # 红色虚线，标记控制点
plt.scatter([P0[0], P1[0], P2[0], P3[0]],
            [P0[1], P1[1], P2[1], P3[1]], color='red', zorder=5) # 红色点，突出控制点

plt.title('Cubic Bezier Curve with NumPy')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True)
plt.legend()
plt.axis('equal') # 保持X和Y轴比例一致
plt.show()

print("前5个曲线上的点：\n", bezier_points[:5])