import numpy as np
from typing import Tuple
from scipy.interpolate import interp1d

def oval_circle(
    start_point: Tuple[float, float],
    angular_direction: float,
    a: float,  # 长半轴
    b: float,  # 短半轴
    points: int = 2000
) -> np.ndarray:
    """
    生成一个完整的椭圆形路径的点，且点之间沿路径的间距近似相等。
    通过线性距离近似弧长来提高计算速度。

    参数:
        start_point: 椭圆的起点坐标 (x, y)。此点位于椭圆的短轴上。
        angular_direction: 椭圆短轴相对于x轴的角度（从起点指向中心的方向），以度为单位。
                           长轴方向垂直于此方向。
        a: 椭圆的长半轴长度。
        b: 椭圆的短半轴长度。
        points: 生成路径上的采样点数量。

    返回:
        一个 N x 2 的 numpy 数组，包含椭圆路径上近似等间距的 x 和 y 坐标。
    """
    if a <= 0 or b <= 0:
        raise ValueError("长半轴和短半轴长度必须为正数。")

    # 将角度转换为弧度
    angular_direction_rad = np.deg2rad(angular_direction)

    # 1. 计算椭圆的中心点
    center_x = start_point[0] + b * np.cos(angular_direction_rad)
    center_y = start_point[1] + b * np.sin(angular_direction_rad)
    center = np.array([center_x, center_y])

    # 2. 长轴方向 (弧度)
    major_axis_direction_rad = angular_direction_rad + np.pi / 2

    # 3. 在高分辨率下生成参数 t 和对应的点
    # 使用比最终点数多得多的点来计算近似弧长
    high_res_factor = 20 # 可根据需要调整，越大越精确但越慢
    high_res_points = points * high_res_factor
    
    # 起始点相对于中心的向量
    dx_start = start_point[0] - center[0]
    dy_start = start_point[1] - center[1]
    
    # 将起点 (dx_start, dy_start) 旋转到标准椭圆坐标系 (长轴为x轴)
    rot_angle_to_standard = -major_axis_direction_rad
    cos_rot = np.cos(rot_angle_to_standard)
    sin_rot = np.sin(rot_angle_to_standard)
    rotated_start_x = dx_start * cos_rot - dy_start * sin_rot
    rotated_start_y = dx_start * sin_rot + dy_start * cos_rot
    
    # 计算起点在标准椭圆坐标系下的参数 t_start
    t_start_standard = np.arctan2(rotated_start_y / b, rotated_start_x / a)
    
    # 生成高分辨率的参数 t，覆盖一个完整的椭圆周期
    t_high_res = np.linspace(t_start_standard, t_start_standard + 2 * np.pi, high_res_points)
    
    # 4. 计算高分辨率下的标准椭圆点
    xs_standard_high_res = a * np.cos(t_high_res)
    ys_standard_high_res = b * np.sin(t_high_res)

    # 5. 旋转并平移高分辨率点
    cos_major = np.cos(major_axis_direction_rad)
    sin_major = np.sin(major_axis_direction_rad)
    # 向量化操作提高速度
    xs_rotated_high_res = xs_standard_high_res * cos_major - ys_standard_high_res * sin_major
    ys_rotated_high_res = xs_standard_high_res * sin_major + ys_standard_high_res * cos_major
    xs_high_res_final = xs_rotated_high_res + center[0]
    ys_high_res_final = ys_rotated_high_res + center[1]

    # 6. 计算近似的累积弦长 (线性距离)
    dx = np.diff(xs_high_res_final)
    dy = np.diff(ys_high_res_final)
    distances = np.sqrt(dx**2 + dy**2)
    s_cumulative = np.concatenate(([0], np.cumsum(distances)))
    total_arc_length_approx = s_cumulative[-1]

    # 7. 在累积弦长上进行等间距采样
    s_equal = np.linspace(0, total_arc_length_approx, points)

    # 8. 使用插值找到与等间距弧长 s_equal 对应的坐标点
    # 对 x 和 y 坐标分别进行插值
    x_interpolator = interp1d(s_cumulative, xs_high_res_final, kind='linear')
    y_interpolator = interp1d(s_cumulative, ys_high_res_final, kind='linear')
    
    xs_final_equal = x_interpolator(s_equal)
    ys_final_equal = y_interpolator(s_equal)

    return np.column_stack((xs_final_equal, ys_final_equal))

# --- 示例用法 ---
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import time

    # 定义参数
    start_point = (1, 1)
    angular_direction = 45  # 短轴方向为 45 度
    a = 3  # 长半轴
    b = 1  # 短轴

    # --- 测试快速版本 ---
    print("计算快速等间距点...")
    start_time = time.time()
    points_equal_fast = oval_circle(start_point, angular_direction, a, b, points=500)
    end_time = time.time()
    print(f"快速版本耗时: {end_time - start_time:.4f} 秒")

    # --- 测试旧的不等间距版本 (用于对比) ---
    print("计算不等间距点...")
    start_time = time.time()
    angular_direction_rad = np.deg2rad(angular_direction)
    center_x = start_point[0] + b * np.cos(angular_direction_rad)
    center_y = start_point[1] + b * np.sin(angular_direction_rad)
    center = np.array([center_x, center_y])
    major_axis_direction_rad = angular_direction_rad + np.pi / 2
    dx_start = start_point[0] - center[0]
    dy_start = start_point[1] - center[1]
    rot_angle_to_standard = -major_axis_direction_rad
    cos_rot = np.cos(rot_angle_to_standard)
    sin_rot = np.sin(rot_angle_to_standard)
    rotated_start_x = dx_start * cos_rot - dy_start * sin_rot
    rotated_start_y = dx_start * sin_rot + dy_start * cos_rot
    t_start_standard = np.arctan2(rotated_start_y / b, rotated_start_x / a)
    t_standard = np.linspace(t_start_standard, t_start_standard + 2 * np.pi, 500)
    xs_standard = a * np.cos(t_standard)
    ys_standard = b * np.sin(t_standard)
    cos_major = np.cos(major_axis_direction_rad)
    sin_major = np.sin(major_axis_direction_rad)
    xs_rotated = xs_standard * cos_major - ys_standard * sin_major
    ys_rotated = xs_standard * sin_major + ys_standard * cos_major
    xs_unequal = xs_rotated + center[0]
    ys_unequal = ys_rotated + center[1]
    end_time = time.time()
    print(f"不等间距版本耗时: {end_time - start_time:.4f} 秒")

    # --- 绘图 ---
    plt.figure(figsize=(15, 5))

    ax1 = plt.subplot(1, 3, 1)
    ax1.plot(xs_unequal, ys_unequal, 'b-', label='不等间距参数化')
    # 为了看清不等间距，只标出几个点
    indices_unequal = np.linspace(0, len(xs_unequal)-1, 20, dtype=int)
    ax1.scatter(xs_unequal[indices_unequal], ys_unequal[indices_unequal], c='blue', s=20, zorder=5)
    ax1.scatter(*start_point, color='red', zorder=10, label=f'起点 {start_point}')
    ax1.set_aspect('equal', adjustable='box')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('不等间距点')
    ax1.legend()
    ax1.grid(True)

    ax2 = plt.subplot(1, 3, 2)
    ax2.plot(points_equal_fast[:, 0], points_equal_fast[:, 1], 'g-', label='快速等间距')
    # 为了看清等间距，只标出几个点
    indices_equal = np.linspace(0, len(points_equal_fast)-1, 20, dtype=int)
    ax2.scatter(points_equal_fast[indices_equal, 0], points_equal_fast[indices_equal, 1], c='green', s=20, zorder=5)
    ax2.scatter(*start_point, color='red', zorder=10, label=f'起点 {start_point}')
    ax2.set_aspect('equal', adjustable='box')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title('快速等间距点')
    ax2.legend()
    ax2.grid(True)
    
    # --- 验证等间距性 ---
    ax3 = plt.subplot(1, 3, 3)
    distances_fast = np.sqrt(np.sum(np.diff(points_equal_fast, axis=0)**2, axis=1))
    ax3.plot(distances_fast, 'g-o', markersize=3, label='快速等间距点间距离')
    ax3.set_xlabel('点对索引')
    ax3.set_ylabel('点间距离')
    ax3.set_title('点间距离验证')
    ax3.legend()
    ax3.grid(True)
    print(f"快速版本点间距离标准差: {np.std(distances_fast):.6f}")

    plt.tight_layout()
    plt.show()




