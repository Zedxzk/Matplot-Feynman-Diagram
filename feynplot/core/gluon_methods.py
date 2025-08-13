from feynplot.core.bezier import *
from feynplot.core.special_curves import *
# from feynplot.core.line import Line, GluonLine  # 确保导入 GluonLine

from feynplot.core.circle import oval_circle

def generate_helix_curve_points_based_on_bezier_path(path_points, radius, n_cycles=15, v=5, loop=False):
    """
    根据给定的贝塞尔路径点，生成沿路径运动且绕路径旋转的点D轨迹。
    - path_points: ndarray，路径上点序列 (N,2)
    - radius: D点绕C点旋转半径
    - n_cycles: 绕圈数（整数）
    - v: C点沿路径速度
    返回: D轨迹点数组 (N, 2)
    """

    path_points = np.array(path_points)
    A = path_points[0]
    B = path_points[-1]

    # 找起点和终点对应圆上的最接近路径点
    if not loop:
        idx_start, vec_start = find_closest_intersection_point(A, radius, path_points)
        idx_end, vec_end = find_closest_intersection_point(B, radius, path_points)
    
    else:
        (idx_start, vec_start), (idx_end, vec_end) = find_closest_intersection_point(A, radius, path_points, loop=True)

    if idx_start > idx_end:
        raise ValueError("index_start should be less or equal to index_end")

    truncated_path = path_points[idx_start:idx_end+1]


    vec_start_angle = np.arctan2(vec_start[1], vec_start[0])
    vec_end_angle = np.arctan2(vec_end[1], vec_end[0])

    path_length = compute_path_length(truncated_path)

    # 检查路径长度和速度是否为零
    if path_length == 0 or v == 0:
        raise ValueError(f'''Path length ({path_length})  greater than zero to compute helix trajectory.
                         Please check the amplitude and wavelength of the gluon line.''')

    total_phase = 2 * np.pi * n_cycles + vec_end_angle - vec_start_angle

    total_time = path_length / v
    omega = total_phase / total_time

    num_steps = len(truncated_path)
    dt = total_time / (num_steps - 1) if num_steps > 1 else 0

    D_trajectory = np.zeros_like(truncated_path)
    for i, point_C in enumerate(truncated_path):
        current_time = i * dt
        phase_D_rel_C = vec_start_angle + omega * current_time
        dx = radius * np.cos(phase_D_rel_C)
        dy = radius * np.sin(phase_D_rel_C)
        D_trajectory[i] = point_C + np.array([dx, dy])

    return truncated_path, D_trajectory




def generate_gluon_helix(line):
    from feynplot.core.line import GluonLine  # 函数内部导入
    if not isinstance(line, GluonLine):
        raise TypeError("line must be a GluonLine instance")
    R = line.amplitude
    n_cycles = line.n_cycles
    v = line.wavelength

    if line.loop:
        # 如果是自环，直接生成椭圆路径
        base_path = oval_circle(
            start_point=(line.v_start.x, line.v_start.y),
            angular_direction=line.angular_direction,
            a=line.a,
            b=line.b,
            points=2000  # 高分辨率
        )

    else:
        start_point = line.v_start
        end_point = line.v_end
        angle_out = line.angleOut
        angle_in = line.angleIn
        bezier_offset = line.bezier_offset

        base_path = generate_bezier_path(start_point, end_point, angle_out, angle_in, offset_ratio=bezier_offset, loop=line.loop)

    # 调用螺旋点生成函数，返回D轨迹点
    truncated_path, D_trajectory = generate_helix_curve_points_based_on_bezier_path(base_path, radius=R, n_cycles=n_cycles, v=v, loop=line.loop)

    return truncated_path, D_trajectory

def generate_gluon_bezier(line):
    from feynplot.core.line import GluonLine  # 只在函数内部导入
    if not isinstance(line, GluonLine):
        raise TypeError("line must be a GluonLine instance")
    start_point = line.v_start
    end_point = line.v_end
    angle_out = line.angleOut
    angle_in = line.angleIn
    bezier_offset = line.bezier_offset
    v = line.wavelength
    R = line.amplitude
    n_cycles = line.n_cycles
    bezier_offset = line.bezier_offset
    bezier_path = generate_bezier_path(start_point, end_point, angle_out, angle_in, offset_ratio=bezier_offset)
    index_start, vector_start = find_closest_intersection_point(start_point, R, bezier_path)
    index_end, vector_end = find_closest_intersection_point(end_point, R, bezier_path)
    if index_start > index_end:
        raise SystemExit("index_start > index_end")
    truncated_path = bezier_path[index_start:index_end+1]
    return truncated_path
