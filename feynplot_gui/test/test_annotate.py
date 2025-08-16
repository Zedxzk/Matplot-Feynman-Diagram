import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import warnings
import math

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------------------------------------------------------
# 1. 自定义箭头：支持 angles，确保起点终点精确
# ------------------------------------------------------------
class SwallowtailArrow(mpatches.ArrowStyle._Base):
    """
    一个自定义的燕尾箭头，其形状由角度定义。
    
    参数：
    - arrow_angle: 箭头尖端的一半角度 (弧度或度数)。
    - tail_angle: 燕尾部分的一半角度 (弧度或度数)。
    - notch_depth_ratio: 凹槽深度与箭头总长度的比例。
    """
    # _style_keys = ("arrow_angle", "tail_angle", "notch_depth_ratio")

    def __init__(self, arrow_angle=30, tail_angle=10, notch_depth_ratio=0.5, direction="right", offset_ratio : float = 0, use_degrees=True):
        super().__init__()
        if use_degrees:
            self.arrow_angle = math.radians(float(arrow_angle))
            self.tail_angle = math.radians(float(tail_angle))
        else:
            self.arrow_angle = float(arrow_angle)
            self.tail_angle = float(tail_angle)
        
        self.offset_ratio = float(offset_ratio)
        self.notch_depth_ratio = float(notch_depth_ratio)
        self.direction = str(direction).lower()

    def transmute(self, path, mutation_size=1, offset_ratio=0):
        # 获取路径的起点和终点，这些是 Matplotlib 转换后的内部显示坐标
        x0, y0 = path.vertices[-1]  # 箭头起点 (xytext)
        x1, y1 = path.vertices[0]   # 箭头终点 (xy)

        # 这里添加了调试输出，显示内部坐标
        print(f"--- 箭头内部调试信息 ---")
        print(f"内部显示坐标: 终点 (xy) = ({x1:.2f}, {y1:.2f})")
        print(f"内部显示坐标: 起点 (xytext) = ({x0:.2f}, {y0:.2f})")
        offset_ratio = self.offset_ratio
        # 计算箭头方向和长度，这部分是你的原始逻辑
        dx, dy = x1 - x0, y1 - y0
        axis_length = math.sqrt(dx**2 + dy**2) 
        print(f"dx: {dx:.2f}, dy: {dy:.2f}, axis_length: {axis_length:.2f}")
        
        # 你的原始逻辑：将轴长度与 mutation_size 结合
        axis_length *= mutation_size / 10
        offset_ratio /= 100
        self.axis_length = axis_length
        if axis_length == 0:
            return Path([(x1, y1), (x1, y1)], [Path.MOVETO, Path.LINETO]), True

        angle = math.atan2(dy, dx)
        
        self.third_angle = self.tail_angle - self.arrow_angle
        tail_length = math.sin(self.arrow_angle) * self.axis_length / math.sin(self.third_angle)

        # 定义基础箭头形状（朝右）
        verts = [
            (0, 0),
            (tail_length * math.cos(math.pi - self.tail_angle + angle), tail_length * math.sin(math.pi - self.tail_angle + angle)),
            (axis_length * math.cos(angle), axis_length * math.sin(angle)),
            (tail_length * math.cos(angle - math.pi + self.tail_angle), tail_length * math.sin(angle - math.pi + self.tail_angle)),
            (0, 0),
        ]

        # 旋转和平移
        main_axis = (axis_length * math.cos(angle), axis_length * math.sin(angle))
        final_verts = []
        
        for x, y in verts:
            final_verts.append((x + x0 + offset_ratio * main_axis[0], y + y0 + offset_ratio * main_axis[1]))
            # 这里的打印是为了显示你原始代码中的最终顶点
            print(f"Final vertex: ({x + x0 + offset_ratio * main_axis[0]:.2f}, {y + y0 + offset_ratio * main_axis[1]:.2f})")

        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        return Path(final_verts, codes), True

# 注册
mpatches.ArrowStyle.register("swallowtail", SwallowtailArrow)

# ------------------------------------------------------------
# 2. 画图
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_title("自定义 Swallowtail 箭头（仅用于调试）", fontsize=16)
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
# 2.1 向右
xy_data = (0.5, 0.5)
xytext_data = (0.9, 0.9)
# 在调用 annotate 之前，先打印数据坐标
# 使用转换器将数据坐标转换为像素坐标
# 这里的坐标是相对于 Figure 窗口左下角的
xy_pixel = ax.transData.transform(xy_data)
xytext_pixel = ax.transData.transform(xytext_data)
print(f"--- 绘图指令 ---")
print(f"数据坐标: xytext={xytext_data}, xy={xy_data}")
print(f"像素坐标: xytext={xytext_pixel}, xy={xy_pixel}")

ax.annotate('向右', xy=xy_data, xytext=xytext_data,
            ha='center', va='center', fontsize=12,
            arrowprops=dict(
                arrowstyle=mpatches.ArrowStyle("swallowtail", 
                                                arrow_angle=30, 
                                                tail_angle=60,
                                                offset_ratio=-100,  # 偏移比例
                                                ),
                facecolor='cornflowerblue',
                edgecolor='navy',
                mutation_scale=2, 
                shrinkA=0,  # 关闭起点收缩
                shrinkB=0   # 关闭终点收缩
                ))

# ------------------------------------------------------------
# 3. 美化
# ------------------------------------------------------------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)

plt.show()