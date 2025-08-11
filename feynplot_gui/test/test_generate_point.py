import numpy as np

def generate_curve_data(npoints=1000):
    """生成基础抛物线数据"""

    # 方法1: 点间距离相等（均匀采样曲线弧长）
    # 首先生成高密度的曲线点用于计算弧长
    x_dense = np.linspace(-2, 2, 10000)
    y_dense = -x_dense**2 + 4
    curve_dense = np.column_stack([x_dense, y_dense])

    # 计算每段的弧长
    deltas = np.diff(curve_dense, axis=0)
    segment_lengths = np.sqrt((deltas**2).sum(axis=1))
    arc_lengths = np.concatenate([[0], np.cumsum(segment_lengths)])
    total_length = arc_lengths[-1]

    # 均匀采样弧长
    target_lengths = np.linspace(0, total_length, npoints)
    x_uniform_arc = np.interp(target_lengths, arc_lengths, x_dense)
    y_uniform_arc = -x_uniform_arc**2 + 4
    uniform_arc = np.column_stack([x_uniform_arc, y_uniform_arc])

    # 方法2: x坐标均匀分布
    x_uniform_x = np.linspace(-2, 2, npoints)
    y_uniform_x = -x_uniform_x**2 + 4
    uniform_x = np.column_stack([x_uniform_x, y_uniform_x])

    # 返回参数t用于x轴均匀分布的情况
    t_uniform = np.linspace(0, 1, npoints)

    return uniform_arc, uniform_x, t_uniform

# 示例调用
uniform_arc, uniform_x, t_uniform = generate_curve_data()

# 打印前几个点验证
print("弧长均匀分布点（前5个）:", uniform_arc[:5])
print("x轴均匀分布点（前5个）:", uniform_x[:5])
print("参数 t（前5个）:", t_uniform[:5])
