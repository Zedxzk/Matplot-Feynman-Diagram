import numpy as np
import matplotlib.pyplot as plt
from numpy import sin, cos, sqrt, pi
plt.rcParams['font.family'] = ['Microsoft YaHei']




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


def compute_tangent(points):
    """计算切线向量"""
    tangents = np.zeros_like(points)
    
    # 计算相邻点的差值
    tangents[:-1] = points[1:] - points[:-1]
    tangents[-1] = points[-1] - points[-2]  # 最后一点使用前一个差值
    
    # 归一化
    norms = np.linalg.norm(tangents, axis=1)
    norms = np.maximum(norms, 1e-8)  # 避免除零
    tangents = tangents / norms[:, np.newaxis]
    
    return tangents

def compute_normal(tangents):
    """计算法线向量 (切线逆时针转90度)"""
    normals = np.zeros_like(tangents)
    normals[:, 0] = -tangents[:, 1]  # -ty
    normals[:, 1] = tangents[:, 0]   # tx
    return normals

def generate_gluon_line(base_path, t_param, nloops=8, xamp=0.3, yamp=0.3, phase=0):
    """
    基于原代码逻辑生成胶子线
    
    参数:
    base_path: 基础路径坐标数组 (N, 2)
    t_param: 参数数组 (N,)
    nloops: 螺旋圈数
    xamp, yamp: x和y方向振幅
    phase: 相位
    """
    
    # 计算切线和法线
    tangents = compute_tangent(base_path)
    normals = compute_normal(tangents)
    
    # 按照原代码的螺旋逻辑
    tau = 2 * pi
    omega = tau * nloops
    phi = tau * phase
    
    # 计算螺旋偏移
    dy = -cos(omega * t_param + phi)
    dx = sin(omega * t_param + phi)
    
    # 去除起始偏移（归零起始点）
    dy = dy - dy[0]
    dx = dx - dx[0]
    
    # 组合切线和法线方向的位移
    dxy = (xamp * tangents * dx[:, np.newaxis] + 
           yamp * normals * dy[:, np.newaxis])
    
    # 最终坐标 = 基础路径 + 螺旋位移
    gluon_path = base_path + dxy
    
    return gluon_path

def plot_comparison():
    """绘制对比图"""
    
    # 生成数据
    uniform_param, uniform_x, t_param = generate_curve_data()   
    amp = 0.4
    # 生成胶子线
    gluon_param = generate_gluon_line(uniform_param, t_param, nloops=8, xamp=amp, yamp=amp)
    gluon_x = generate_gluon_line(uniform_x, t_param, nloops=8, xamp=amp, yamp=amp)
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 左图：均匀参数分布
    ax1.plot(uniform_param[:, 0], uniform_param[:, 1], '--', color='gray', alpha=0.5, label='原始抛物线')
    ax1.plot(gluon_param[:, 0], gluon_param[:, 1], 'r-', linewidth=2, label='胶子线 (均匀参数)')
    ax1.set_title('均匀参数分布\n(点沿弧长均匀分布)')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_aspect('equal')
    
    # 右图：均匀x坐标分布
    ax2.plot(uniform_x[:, 0], uniform_x[:, 1], '--', color='gray', alpha=0.5, label='原始抛物线')
    ax2.plot(gluon_x[:, 0], gluon_x[:, 1], 'b-', linewidth=2, label='胶子线 (均匀x坐标)')
    ax2.set_title('均匀x坐标分布\n(点按x坐标均匀分布)')
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.show()
    
    return uniform_param, uniform_x, gluon_param, gluon_x

def interactive_test():
    """交互式参数测试"""
    
    # 生成基础数据
    uniform_param, uniform_x, t_param = generate_curve_data()
    
    # 测试不同参数
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('胶子线参数效果测试 (y = -x² + 4, x ∈ [-2, 2])', fontsize=16)
    
    # 测试不同螺旋圈数
    for i, nloops in enumerate([4, 8, 12]):
        gluon = generate_gluon_line(uniform_param, t_param, nloops=nloops, xamp=0.1, yamp=0.1)
        axes[0, i].plot(uniform_param[:, 0], uniform_param[:, 1], '--', color='gray', alpha=0.5)
        axes[0, i].plot(gluon[:, 0], gluon[:, 1], 'r-', linewidth=2)
        axes[0, i].set_title(f'螺旋圈数 = {nloops}')
        axes[0, i].grid(True, alpha=0.3)
        axes[0, i].set_aspect('equal')
    
    # 测试不同振幅
    for i, amp in enumerate([0.05, 0.1, 0.2]):
        gluon = generate_gluon_line(uniform_param, t_param, nloops=8, xamp=amp, yamp=amp)
        axes[1, i].plot(uniform_param[:, 0], uniform_param[:, 1], '--', color='gray', alpha=0.5)
        axes[1, i].plot(gluon[:, 0], gluon[:, 1], 'b-', linewidth=2)
        axes[1, i].set_title(f'振幅 = {amp}')
        axes[1, i].grid(True, alpha=0.3)
        axes[1, i].set_aspect('equal')
    
    plt.tight_layout()
    plt.show()

def analyze_distribution_difference():
    """分析两种分布方式的差异"""
    
    uniform_param, uniform_x, t_param = generate_curve_data()
    
    # 计算点间距离
    def point_distances(points):
        diffs = points[1:] - points[:-1]
        distances = np.linalg.norm(diffs, axis=1)
        return distances
    
    dist_param = point_distances(uniform_param)
    dist_x = point_distances(uniform_x)
    
    plt.figure(figsize=(12, 8))
    
    # 子图1：点分布对比
    plt.subplot(2, 2, 1)
    plt.plot(uniform_param[:, 0], uniform_param[:, 1], 'r-', label='均匀参数分布', linewidth=2)
    plt.plot(uniform_x[:, 0], uniform_x[:, 1], 'b-', label='均匀x坐标分布', linewidth=2)
    plt.title('基础抛物线对比')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    # 子图2：点间距离分析
    plt.subplot(2, 2, 2)
    plt.plot(dist_param, 'r-', label='均匀参数 - 点间距', alpha=0.8)
    plt.plot(dist_x, 'b-', label='均匀x坐标 - 点间距', alpha=0.8)
    plt.title('相邻点间距离')
    plt.xlabel('点索引')
    plt.ylabel('距离')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图3&4：胶子线效果
    gluon_param = generate_gluon_line(uniform_param, t_param, nloops=10, xamp=0.12, yamp=0.12)
    gluon_x = generate_gluon_line(uniform_x, t_param, nloops=10, xamp=0.12, yamp=0.12)
    
    plt.subplot(2, 2, 3)
    plt.plot(uniform_param[:, 0], uniform_param[:, 1], '--', color='gray', alpha=0.5)
    plt.plot(gluon_param[:, 0], gluon_param[:, 1], 'r-', linewidth=2)
    plt.title('胶子线 - 均匀参数分布')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    plt.subplot(2, 2, 4)
    plt.plot(uniform_x[:, 0], uniform_x[:, 1], '--', color='gray', alpha=0.5)
    plt.plot(gluon_x[:, 0], gluon_x[:, 1], 'b-', linewidth=2)
    plt.title('胶子线 - 均匀x坐标分布')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    plt.tight_layout()
    plt.show()
    
    print("=== 分析结果 ===")
    print(f"均匀参数分布 - 平均点间距: {np.mean(dist_param):.6f}")
    print(f"均匀参数分布 - 点间距标准差: {np.std(dist_param):.6f}")
    print(f"均匀x坐标分布 - 平均点间距: {np.mean(dist_x):.6f}")
    print(f"均匀x坐标分布 - 点间距标准差: {np.std(dist_x):.6f}")
    
    return uniform_param, uniform_x, gluon_param, gluon_x

# 运行测试
if __name__ == "__main__":
    print("正在生成胶子线测试...")
    
    # 基本对比
    print("\n1. 基本对比测试")
    plot_comparison()
    
    # 参数效果测试
    print("\n2. 参数效果测试")
    interactive_test()
    
    # 详细分析
    print("\n3. 分布差异分析")
    results = analyze_distribution_difference()
    
    print("\n测试完成！")