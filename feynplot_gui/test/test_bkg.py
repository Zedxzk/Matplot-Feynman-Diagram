import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import colorConverter

def plot_chessboard_background(ax, size=0.5, color1='white', color2='#D3D3D3'):
    """
    在 Matplotlib Axes 的后面绘制一个灰白相间的棋盘格背景。
    
    参数：
    ax (matplotlib.axes.Axes): 要在其上绘制的 Axes 对象。
    size (float): 每个棋盘格的大小（单位：数据单位）。
    color1 (str): 第一个棋盘格颜色。
    color2 (str): 第二个棋盘格颜色（默认是灰色）。
    """
    # 获取 Axes 的数据坐标范围
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # 将颜色转换为 RGBA 格式
    c1 = colorConverter.to_rgba(color1)
    c2 = colorConverter.to_rgba(color2)

    # 创建一个列表来存储所有棋盘格
    patches = []

    # 循环绘制棋盘格
    for x in range(int(xlim[0] / size), int(xlim[1] / size) + 1):
        for y in range(int(ylim[0] / size), int(ylim[1] / size) + 1):
            # 根据坐标的奇偶性选择颜色
            color = c1 if (x + y) % 2 == 0 else c2
            
            # 创建一个矩形补丁，并添加到列表中
            rect = Rectangle((x * size, y * size), size, size, facecolor=color)
            patches.append(rect)

    # 将所有补丁添加到 Axes 中
    # 使用 zorder=-1 确保棋盘格在所有其他绘图元素之后
    for patch in patches:
        ax.add_patch(patch)
        patch.set_zorder(-1)

    # 重新设置坐标轴范围，以防绘制的格子改变了视图
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # 确保 Axes 的背景是透明的
    ax.patch.set_alpha(0.0)

# --- 绘图示例 ---
if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(8, 6))

    # 绘制棋盘格背景
    plot_chessboard_background(ax)

    # 绘制你的数据
    ax.plot([1, 2, 3, 4], [2, 5, 3, 6], 'o-', label='Data')
    ax.set_title("带有棋盘格背景的透明图表")
    ax.set_xlabel("X轴")
    ax.set_ylabel("Y轴")
    ax.legend()

    plt.show()