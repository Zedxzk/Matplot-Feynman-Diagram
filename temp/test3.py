import matplotlib.pyplot as plt
import numpy as np

def add_checkerboard_background(fig, ax, square_size=20, n_squares=40):
    """
    给 Matplotlib Axes 添加棋盘格背景，显示时可视化透明区域。
    """
    # 生成棋盘格：0 和 1 交替
    checker = np.indices((n_squares, n_squares)).sum(axis=0) % 2
    checker = np.kron(checker, np.ones((square_size, square_size)))
    
    # 在 ax 上画棋盘格，放在最底层
    ax.imshow(checker, cmap="gray", vmin=0, vmax=1,
              extent=[*ax.get_xlim(), *ax.get_ylim()],
              aspect='auto', alpha=0.3, zorder=-100)

    # 去掉 Axes 白色背景
    ax.patch.set_alpha(0)

# 示例
x = np.linspace(0, 10, 200)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y, lw=3)

# 添加棋盘格背景
# add_checkerboard_background(fig, ax)

plt.show()

# 保存时仍然是真透明
fig.savefig("out.svg", transparent=True)
