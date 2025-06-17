import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

def draw_custom_hatch_circle(
    ax, 
    center_x, 
    center_y, 
    radius=0.5, 
    facecolor='lightgray', 
    edgecolor='black', 
    linewidth=1.5, 
    alpha=1.0, 
    zorder=2,
    
    # 自定义阴影参数
    hatch_line_color='black',  # 阴影线的颜色
    hatch_line_width=2,      # 阴影线的线宽 (可控制)
    hatch_line_angle_deg=45,   # 阴影线的倾斜角度 (可控制，度数)
    hatch_spacing_ratio=0.1,   # 阴影线之间的间距 (相对于半径的比例)
    
    label=None,
    label_offset=(0.1, 0.1),
    label_size=12,
    **kwargs
):
    """
    绘制一个带自定义斜线阴影的圆圈，阴影线会被精确裁剪到圆圈内部。
    """
    # 1. 绘制圆圈 (作为背景和边框)
    circle = Circle(
        (center_x, center_y),
        radius=radius,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha,
        zorder=zorder,
        **kwargs
    )
    ax.add_patch(circle)

    # 2. 为阴影线创建裁剪路径
    # 使用圆形的路径作为裁剪对象
    # 注意：一个 patch 对象自身就可以作为另一个 artist 的 clip_path
    clip_path_circle = Circle(
        (center_x, center_y),
        radius=radius,
        transform=ax.transData # 确保转换与数据坐标系一致
    )
    # 我们不需要将 clip_path_circle 添加到 ax，它只用于裁剪
    # 但它的 .patch 属性是实际的 Path 对象
    
    # --- 绘制自定义斜线阴影 ---
    angle_rad = np.deg2rad(hatch_line_angle_deg) # 将角度转换为弧度
    
    # 计算阴影线的间距
    # 间距现在是基于圆周长或者直径来计算，使得线条数量相对稳定
    spacing = radius * hatch_spacing_ratio
    
    # 计算需要覆盖整个圆的线段范围
    # 最大的对角线长度，用于确保线条足够长以覆盖整个圆
    max_dist = np.sqrt(2 * radius**2) * 1.5 # 增加一点余量
    
    # 沿着与阴影线垂直的方向计算起始位置
    # 这个循环生成一系列平行线
    for i in np.arange(-max_dist, max_dist, spacing):
        # 计算线的两个端点，它们位于一个比圆大一些的矩形范围内
        # 这里的计算是为了生成一个足够大的线段，它肯定会穿过圆形
        
        # 线的中心点，沿着垂直于 hatch_line_angle_deg 的方向移动
        # 从圆心开始偏移 i 距离，然后旋转到正确的角度
        
        # 计算线的两个端点在未旋转坐标系中的位置 (水平线)
        # 确保线足够长，能覆盖整个圆形
        p1 = np.array([-max_dist, i])
        p2 = np.array([max_dist, i])
        
        # 旋转这些点到期望的角度，并平移到圆心
        cos_theta = np.cos(angle_rad)
        sin_theta = np.sin(angle_rad)

        rotated_p1_x = center_x + p1[0] * cos_theta - p1[1] * sin_theta
        rotated_p1_y = center_y + p1[0] * sin_theta + p1[1] * cos_theta

        rotated_p2_x = center_x + p2[0] * cos_theta - p2[1] * sin_theta
        rotated_p2_y = center_y + p2[0] * sin_theta + p2[1] * cos_theta

        # 绘制线段
        line_artist, = ax.plot(
            [rotated_p1_x, rotated_p2_x],
            [rotated_p1_y, rotated_p2_y],
            color=hatch_line_color,
            linewidth=hatch_line_width,
            zorder=zorder + 0.5 # 阴影线在圆圈上方
        )
        
        # 关键步骤：将圆形的 Patch 路径设置为线的裁剪路径
        line_artist.set_clip_path(circle) # 使用前面创建的 'circle' patch 进行裁剪
                                          # 或者如果你更喜欢使用临时的 Path 对象
                                          # line_artist.set_clip_path(clip_path_circle)

    # 绘制标签 (如果提供)
    if label:
        ax.text(
            center_x + label_offset[0],
            center_y + label_offset[1],
            label,
            ha='center',
            va='center',
            fontsize=label_size,
            zorder=zorder + 1 # 确保标签在圆圈和阴影之上
        )

# --- 示例使用 ---
if __name__ == "__main__":
    import mplhep as hep
    plt.style.use(hep.style.CMS)
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.family'] = "Times New Roman"
    # plt.rcParams['text.usetex'] = True

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal', adjustable='box')
    ax.set_axis_off()

    # 使用 Matplotlib 内置 hatch (线宽和角度固定)
    circle1 = Circle(
        (0, 0), radius=0.8, facecolor='lightblue', edgecolor='blue', 
        linewidth=2, hatch='///', alpha=0.8, zorder=2
    )
    ax.add_patch(circle1)
    ax.text(0, 0.9, 'Default Hatch', ha='center', va='center', fontsize=12, zorder=3)

    # 使用自定义函数绘制阴影 (可控制线宽和角度)，并正确裁剪
    draw_custom_hatch_circle(
        ax, 
        center_x=3, 
        center_y=0, 
        radius=0.9, 
        facecolor='lightgreen', 
        edgecolor='darkgreen', 
        linewidth=2.5, 
        alpha=0.9,
        
        hatch_line_color='red',     # 红色阴影线
        hatch_line_width=2.0,       # 阴影线较粗
        hatch_line_angle_deg=30,    # 倾斜 30 度
        hatch_spacing_ratio=0.15,   # 间距更大 (相对于半径)
        
        label=r'Custom\,Hatch',
        label_offset=(0, -1.0),
        label_size=14
    )

    # 另一个自定义阴影，不同角度和颜色
    draw_custom_hatch_circle(
        ax, 
        center_x=6, 
        center_y=0, 
        radius=0.7, 
        facecolor='lavender', 
        edgecolor='purple', 
        linewidth=1.0, 
        alpha=0.7,
        
        hatch_line_color='black',   # 黑色阴影线
        hatch_line_width=0.4,       # 阴影线较细
        hatch_line_angle_deg=-60,   # 倾斜 -60 度
        hatch_spacing_ratio=0.1,    # 间距适中
        
        label=r'Custom\,Hatch$_2$',
        label_offset=(0.8, 0.0),
        label_size=12
    )


    ax.set_xlim(-1.5, 7.5)
    ax.set_ylim(-1.5, 1.5)
    plt.title('Matplotlib 自定义圆形阴影示例 (已裁剪)')
    plt.tight_layout()
    plt.show()