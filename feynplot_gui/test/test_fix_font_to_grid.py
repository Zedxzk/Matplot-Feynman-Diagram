import matplotlib.pyplot as plt
from typing import Tuple
plt.rcParams['font.family'] = 'SImHei' # 使用中易黑体
def get_scaled_fontsize_factor(ax: plt.Axes) -> float:
    """
    计算一个缩放因子，用于将字体大小（点）映射到数据单位。
    此函数以ax的较小一侧为标准。

    Args:
        ax: Matplotlib 的 Axes 对象。

    Returns:
        缩放因子，将字体大小（点）乘以该因子即可得到数据单位的宽度。
    """
    fig = ax.figure
    if fig is None:
        raise ValueError("Axes must be associated with a Figure.")

    # 获取画布的物理尺寸（英寸）和 DPI
    fig_width_inch, fig_height_inch = fig.get_size_inches()
    dpi = fig.get_dpi()

    # 获取数据范围
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    data_range_x = xlim[1] - xlim[0]
    data_range_y = ylim[1] - ylim[0]

    # 计算每英寸对应的点数（1点 = 1/72英寸）
    points_per_inch = 72

    # 计算x和y轴上，每数据单位对应的英寸数
    # 如果数据范围为0，则避免除以0错误
    if data_range_x > 0:
        inch_per_data_x = fig_width_inch / data_range_x
    else:
        inch_per_data_x = float('inf') # 无穷大

    if data_range_y > 0:
        inch_per_data_y = fig_height_inch / data_range_y
    else:
        inch_per_data_y = float('inf') # 无穷大

    # 选择较小一侧作为标准
    if inch_per_data_x < inch_per_data_y:
        # x轴是较小的一侧，每数据单位的英寸数更小
        # 这意味着在相同点数下，x轴上的字符会更“宽”
        inch_per_data = inch_per_data_x
    else:
        # y轴是较小的一侧
        inch_per_data = inch_per_data_y

    # 缩放因子 = (1/points_per_inch) / inch_per_data
    # 该因子表示一个点单位对应的英寸数除以每数据单位对应的英寸数
    # 结果就是1点对应的点单位数
    return (1 / points_per_inch) / inch_per_data


if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(6, 8), dpi=100)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50) # y轴范围较小
    ax.set_aspect('equal', adjustable='box')

    # 获取缩放因子
    scale_factor = get_scaled_fontsize_factor(ax)

    # 绘制一个宽度为5数据单位的文本
    target_data_units = 5.0
    fontsize_in_points = target_data_units / scale_factor
    ax.text(50, 25, "Hello World", ha='center', va='center', fontsize=fontsize_in_points)
    
    # 绘制一个参考矩形，宽度为5
    ax.add_patch(plt.Rectangle((50 - 2.5, 25 - 2.5), 5, 5, color='red', alpha=0.3))

    ax.set_title("文字大小随较小一侧自动缩放")
    plt.show()
    
    # 改变画布尺寸和DPI后，验证是否依然有效
    fig2, ax2 = plt.subplots(figsize=(5, 10), dpi=200) # 故意让y轴变得更小
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.axvline(75, color='black') # 为比较，添加垂直参考线
    ax2.set_aspect('equal', adjustable='box')

    # 重新获取缩放因子
    scale_factor2 = get_scaled_fontsize_factor(ax2)

    # 绘制同样宽度为5数据单位的文本
    fontsize_in_points2 = target_data_units / scale_factor2
    ax2.text(50, 25, "Hello World", ha='center', va='center', fontsize=fontsize_in_points2)

    # 绘制参考矩形
    ax2.add_patch(plt.Rectangle((50 - 2.5, 25 - 2.5), 5, 5, color='red', alpha=0.3))

    ax2.set_title("改变后，文字大小依然随较小一侧自动缩放")
    plt.show()