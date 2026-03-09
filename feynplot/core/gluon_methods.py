from feynplot.core.bezier import *
from feynplot.core.special_curves import *

from feynplot.core.circle import oval_circle


def _cumulative_path_length(path):
    """路径各点到起点的弧长，path 形状 (N,2)，返回长度 N，cum[0]=0。"""
    diffs = np.diff(path, axis=0)
    seg_lens = np.linalg.norm(diffs, axis=1)
    cum = np.zeros(len(path))
    cum[1:] = np.cumsum(seg_lens)
    return cum


def generate_helix_curve_points_based_on_bezier_path(
    path_points,
    radius,
    n_cycles=15,
    v=5,
    loop=False,
    clockwise: bool = False,
    squash_ratio: float = 1.0,
    start_straight_ratio: float = 0.0,
    end_straight_ratio: float = 0.0,
):
    """
    根据给定的贝塞尔路径点，生成沿路径运动且绕路径旋转的点 D 轨迹。
    若 start_straight_ratio 或 end_straight_ratio 不为 0：按比例截出中间段，将两比例置 0 后递归，
    再拼接 [A,P1] + 递归得到的螺旋轨迹 + [P2,B] 返回。
    返回: (truncated_path, full_trajectory)。
    """
    path_points = np.array(path_points)
    A = path_points[0]
    B = path_points[-1]

    if not loop:
        idx_start, vec_start = find_closest_intersection_point(A, radius, path_points)
        idx_end, vec_end = find_closest_intersection_point(B, radius, path_points)
    else:
        (idx_start, vec_start), (idx_end, vec_end) = find_closest_intersection_point(A, radius, path_points, loop=True)

    if idx_start > idx_end:
        idx_start, idx_end = idx_end, idx_start

    truncated_path = path_points[idx_start:idx_end + 1]
    num_steps = len(truncated_path)
    if num_steps < 2:
        return truncated_path, truncated_path.copy()

    path_length = float(compute_path_length(truncated_path))
    if path_length == 0 or v == 0:
        raise ValueError(
            "Path length ({}) and speed (v) must be greater than zero to compute helix trajectory. "
            "Please check the amplitude and wavelength of the gluon line.".format(path_length)
        )

    start_ratio = max(0.0, min(1.0, float(start_straight_ratio)))
    end_ratio = max(0.0, min(1.0, float(end_straight_ratio)))
    if start_ratio + end_ratio >= 1.0:
        start_ratio, end_ratio = 0.0, 0.0

    if start_ratio > 0 or end_ratio > 0:
        cum = _cumulative_path_length(truncated_path)
        L = path_length
        s_start = start_ratio * L
        s_end = (1.0 - end_ratio) * L
        idx_spiral_start = np.searchsorted(cum, s_start, side="left")
        idx_spiral_start = min(idx_spiral_start, num_steps - 2)
        idx_spiral_end = np.searchsorted(cum, s_end, side="right") - 1
        idx_spiral_end = max(idx_spiral_end, idx_spiral_start + 1)
        # 只有一端非零时，螺旋路径延伸到该端顶点，不在该端截断贝塞尔
        mid_segment = truncated_path[idx_spiral_start : idx_spiral_end + 1]
        if start_ratio == 0 and end_ratio > 0:
            spiral_path = np.vstack([np.atleast_2d(A), mid_segment])
        elif start_ratio > 0 and end_ratio == 0:
            spiral_path = np.vstack([mid_segment, np.atleast_2d(B)])
        else:
            spiral_path = mid_segment
        P1 = np.asarray(spiral_path[0])
        P2 = np.asarray(spiral_path[-1])
        _, full_inner = generate_helix_curve_points_based_on_bezier_path(
            spiral_path,
            radius=radius,
            n_cycles=n_cycles,
            v=v,
            loop=loop,
            clockwise=clockwise,
            squash_ratio=squash_ratio,
            start_straight_ratio=0.0,
            end_straight_ratio=0.0,
        )
        parts = []
        if start_ratio > 0:
            parts.append(np.atleast_2d(A))
            parts.append(np.atleast_2d(P1))
        else:
            parts.append(np.atleast_2d(A))
        parts.append(full_inner)
        if end_ratio > 0:
            parts.append(np.atleast_2d(P2))
            parts.append(np.atleast_2d(B))
        elif end_ratio == 0:
            # 末端未设直线比例时仍要连到顶点 B
            parts.append(np.atleast_2d(B))
        full_trajectory = np.vstack(parts)
        return truncated_path, full_trajectory

    vec_start_angle = np.arctan2(vec_start[1], vec_start[0])
    vec_end_angle = np.arctan2(vec_end[1], vec_end[0])
    total_phase = 2 * np.pi * n_cycles + vec_end_angle - vec_start_angle
    if clockwise:
        total_phase = -total_phase
    total_time = path_length / v
    omega = total_phase / total_time
    dt = total_time / (num_steps - 1) if num_steps > 1 else 0.0

    D_trajectory = np.zeros_like(truncated_path)
    for i, point_C in enumerate(truncated_path):
        t_i = i * dt
        phase_D_rel_C = vec_start_angle + omega * t_i
        dx = radius * np.cos(phase_D_rel_C)
        dy = radius * float(squash_ratio) * np.sin(phase_D_rel_C)
        D_trajectory[i] = point_C + np.array([dx, dy])
    return truncated_path, D_trajectory


def generate_gluon_helix(line):
    from feynplot.core.line import GluonLine
    if not isinstance(line, GluonLine):
        raise TypeError("line must be a GluonLine instance")
    R = line.amplitude
    n_cycles = line.n_cycles
    v = line.wavelength
    clockwise = getattr(line, "clockwise", False)
    squash_ratio = getattr(line, "squash_ratio", 1.0)

    if line.loop:
        base_path = oval_circle(
            start_point=(line.v_start.x, line.v_start.y),
            angular_direction=line.angular_direction,
            a=line.a,
            b=line.b,
            points=2000
        )
    else:
        base_path = generate_bezier_path(
            line.v_start, line.v_end,
            line.angleOut, line.angleIn,
            offset_ratio=line.bezier_offset,
            loop=line.loop
        )

    start_straight_ratio = getattr(line, "start_straight_ratio", 0.0)
    end_straight_ratio = getattr(line, "end_straight_ratio", 0.0)
    truncated_path, full_trajectory = generate_helix_curve_points_based_on_bezier_path(
        base_path,
        radius=R,
        n_cycles=n_cycles,
        v=v,
        loop=line.loop,
        clockwise=clockwise,
        squash_ratio=squash_ratio,
        start_straight_ratio=start_straight_ratio,
        end_straight_ratio=end_straight_ratio,
    )
    return truncated_path, full_trajectory

def generate_gluon_bezier(line):
    from feynplot.core.line import GluonLine
    if not isinstance(line, GluonLine):
        raise TypeError("line must be a GluonLine instance")
    start_point = line.v_start
    end_point = line.v_end
    angle_out = line.angleOut
    angle_in = line.angleIn
    bezier_offset = line.bezier_offset
    R = line.amplitude
    bezier_path = generate_bezier_path(start_point, end_point, angle_out, angle_in, offset_ratio=bezier_offset)
    index_start, _ = find_closest_intersection_point(start_point, R, bezier_path)
    index_end, _ = find_closest_intersection_point(end_point, R, bezier_path)
    if index_start > index_end:
        index_start, index_end = index_end, index_start
    truncated_path = bezier_path[index_start:index_end+1]
    return truncated_path
