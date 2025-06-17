import matplotlib.pyplot as plt
import mplhep as hep
from matplotlib.patches import Circle

# 应用你的全局样式设置 (如果需要的话)
plt.style.use(hep.style.CMS)
plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['font.family'] = "Times New Roman"
# plt.rcParams['text.usetex'] = True


def draw_structured_vertex(
    ax, 
    center_x, 
    center_y, 
    radius=0.5, 
    facecolor='lightgray', # 圆的填充颜色
    edgecolor='black',     # 圆的边框和阴影线的颜色
    linewidth=1.5,         # 圆的边框线宽
    hatch_pattern='/',     # 阴影图案，例如 '/' (斜线), '\\' (反斜线), '+' (十字), 'x' (交叉)
    alpha=1.0,             # 透明度
    zorder=2,              # 绘图层级，确保在其他线条之上
    label=None,            # 顶点的标签
    label_offset=(0.1, 0.1), # 标签偏移
    label_size=12,         # 标签字体大小
    **kwargs               # 允许传入更多 Circle 的参数
):
    """
    在 Matplotlib 轴上绘制一个带填充颜色和斜线阴影的圆圈，表示有结构的相互作用顶点。

    参数:
        ax: Matplotlib 的 Axes 对象。
        center_x (float): 圆心的 X 坐标。
        center_y (float): 圆心的 Y 坐标。
        radius (float): 圆的半径。
        facecolor (str): 圆的填充颜色。
        edgecolor (str): 圆的边框和阴影线的颜色。
        linewidth (float): 圆的边框线宽。
        hatch_pattern (str): 用于阴影的图案字符串。
        alpha (float): 圆的透明度 (0.0 到 1.0)。
        zorder (int): 绘图层级。
        label (str, optional): 顶点的文本标签。
        label_offset (tuple, optional): 标签相对于圆心的偏移量。
        label_size (int, optional): 标签的字体大小。
        **kwargs: 任何额外传递给 matplotlib.patches.Circle 的关键字参数。
    """
    # 创建圆形 Patch
    circle = Circle(
        (center_x, center_y),
        radius=radius,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        hatch=hatch_pattern, # 应用阴影
        alpha=alpha,
        zorder=zorder,
        **kwargs
    )
    
    # 将圆形添加到轴上
    ax.add_patch(circle)

    # 绘制标签 (如果提供)
    if label:
        ax.text(
            center_x + label_offset[0],
            center_y + label_offset[1],
            label,
            ha='center',
            va='center',
            fontsize=label_size,
            zorder=zorder + 1 # 确保标签在圆圈之上
        )

# --- 示例使用 ---
if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal', adjustable='box')
    ax.set_axis_off() # 隐藏坐标轴

    # 绘制一个普通的顶点
    ax.plot(0, 0, 'o', color='black', markersize=8, zorder=1, label='普通顶点')

    # 绘制一个带斜线阴影的结构化顶点
    draw_structured_vertex(
        ax, 
        center_x=2, 
        center_y=0, 
        radius=0.7, 
        facecolor='lightblue', 
        edgecolor='darkblue', 
        linewidth=2, 
        hatch_pattern='///', # 更密的斜线
        label=r'$V_{struct}$',
        label_offset=(0.0, 0.9), # 标签放圆上方
        label_size=14
    )

    # 绘制另一个不同阴影和颜色的结构化顶点
    draw_structured_vertex(
        ax, 
        center_x=4.5, 
        center_y=0.5, 
        radius=0.9, 
        facecolor='lightgreen', 
        edgecolor='darkgreen', 
        linewidth=1.8, 
        hatch_pattern='x', # 交叉阴影
        alpha=0.8,
        label=r'$H \rightarrow gg$',
        label_offset=(-0.1, -1.0), # 标签放圆下方
        label_size=16
    )
    
    # 也可以在顶点类中直接集成这个绘制方法
    # 假设你的 Vertex 类有 x, y 坐标
    # struct_v_class = YourVertexClass(x=7, y=0.2, type='structured')
    # draw_structured_vertex(ax, struct_v_class.x, struct_v_class.y, ...)

    ax.set_xlim(-1, 8)
    ax.set_ylim(-2, 2)
    plt.title('带有结构化相互作用顶点的费曼图示例')
    plt.tight_layout()
    plt.show()