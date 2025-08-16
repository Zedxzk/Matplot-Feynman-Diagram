import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import math

class FishtailArrow(mpatches.ArrowStyle._Base):
    """
    一个自定义的鱼尾箭头，其形状由角度定义。
    
    参数：
    - arrow_angle: 箭头尖端的一半角度 (弧度或度数)。
    - tail_angle: 鱼尾部分的一半角度 (弧度或度数)。
    """
    def __init__(self, arrow_angle=60, tail_angle=30, offset_ratio : float = 0, use_degrees=True):
        super().__init__()
        if use_degrees:
            self.arrow_angle = math.radians(float(arrow_angle))
            self.tail_angle = math.radians(float(tail_angle))
        else:
            self.arrow_angle = float(arrow_angle)
            self.tail_angle = float(tail_angle)
        
        self.offset_ratio = float(offset_ratio)

    def transmute(self, path, mutation_size=1, offset_ratio=0):
        x0, y0 = path.vertices[-1]  # 箭头起点 (xytext)
        x1, y1 = path.vertices[0]   # 箭头终点 (xy)
        offset_ratio = self.offset_ratio

        dx, dy = x1 - x0, y1 - y0
        axis_length = 1
        
        axis_length *= mutation_size / 10
        offset_ratio /= 100
        self.axis_length = axis_length
        if axis_length == 0:
            return Path([(x1, y1), (x1, y1)], [Path.MOVETO, Path.LINETO]), True

        angle = math.atan2(dy, dx)
        self.third_angle = self.tail_angle - self.arrow_angle
        tail_length = math.sin(self.arrow_angle) * self.axis_length / math.sin(self.third_angle)

        verts = [
            (0, 0),
            (tail_length * math.cos(math.pi - self.tail_angle + angle), tail_length * math.sin(math.pi - self.tail_angle + angle)),
            (axis_length * math.cos(angle), axis_length * math.sin(angle)),
            (tail_length * math.cos(angle - math.pi + self.tail_angle), tail_length * math.sin(angle - math.pi + self.tail_angle)),
            (0, 0),
        ]

        main_axis = (axis_length * math.cos(angle), axis_length * math.sin(angle))
        final_verts = []
        
        for x, y in verts:
            final_verts.append((x + x0 + offset_ratio * main_axis[0], y + y0 + offset_ratio * main_axis[1]))
        
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        return Path(final_verts, codes), True

# 注册你的自定义箭头样式
mpatches.ArrowStyle.register("fishtail", FishtailArrow)

if __name__ == "__main__":
    # --- 绘图示例 ---
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("自定义鱼尾箭头颜色示例")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.grid(True)

    # 示例 1: 同时设置 facecolor 和 edgecolor
    ax.annotate("绿色填充，蓝色描边",
                xy=(8, 8), xytext=(2, 2),
                arrowprops=dict(
                    arrowstyle="fishtail,arrow_angle=60,tail_angle=30",
                    connectionstyle="arc3,rad=0.3",
                    facecolor="green",       # 设置填充颜色
                    edgecolor="blue",        # 设置轮廓线颜色
                    lw=2                     # 设置线条宽度
                ))

    # 示例 2: 只设置 color，它会同时应用于填充和轮廓
    ax.annotate("红色箭头",
                xy=(8, 2), xytext=(2, 8),
                arrowprops=dict(
                    arrowstyle="fishtail,arrow_angle=60,tail_angle=30",
                    connectionstyle="arc3,rad=-0.3",
                    color="red",             # 颜色同时应用于填充和轮廓
                    lw=2
                ))

    # 示例 3: 无填充，只有轮廓线
    ax.annotate("只有轮廓线的箭头",
                xy=(5, 9), xytext=(5, 5),
                arrowprops=dict(
                    arrowstyle="fishtail,arrow_angle=60,tail_angle=30",
                    facecolor="none",        # 设置为 "none" 或 "white" 来去除填充
                    edgecolor="black",       # 设置轮廓线颜色
                    lw=2
                ))

    plt.show()