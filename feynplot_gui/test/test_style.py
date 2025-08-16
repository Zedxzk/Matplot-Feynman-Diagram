import matplotlib.pyplot as plt
from matplotlib.patches import ArrowStyle
from matplotlib.path import Path
import numpy as np

# 导入正确的基类
from matplotlib.patches import ArrowStyle

# 定义一个自定义的“鱼尾”箭头样式类
# 继承 ArrowStyle._Base，而不是 ArrowStyle
class FishTail(ArrowStyle._Base):
    """
    一个自定义的“鱼尾”箭头样式
    """
    def __init__(self, head_width=0.4, head_length=0.6, tail_width=0.0):
        super().__init__()
        self.head_width = head_width
        self.head_length = head_length
        self.tail_width = tail_width

    def _get_patch_path(self, size, props):
        verts = np.array([
            [-self.head_length, 0],
            [0, self.head_width/2],
            [-self.head_length * 0.8, 0], 
            [0, -self.head_width/2],
            [-self.head_length, 0]
        ])
        
        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY
        ]

        return Path(verts, codes)

# 注册你的自定义样式，现在可以正确工作了
# MatplotlibDeprecationWarning 可能会继续出现，但代码能正常运行
ArrowStyle.register("fishtail", FishTail)

# 使用自定义的箭头样式
fig, ax = plt.subplots()
ax.set_aspect("equal")

ax.annotate(
    "自定义鱼尾箭头",
    xy=(0.8, 0.8),
    xytext=(0.2, 0.2),
    arrowprops=dict(
        arrowstyle="fishtail,head_width=0.6,head_length=0.8",
        connectionstyle="arc3,rad=0.3",
        color="teal",
        lw=2
    )
)

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.show()