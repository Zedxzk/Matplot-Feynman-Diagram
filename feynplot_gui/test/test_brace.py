import matplotlib.pyplot as plt

# 创建图形
fig, ax = plt.subplots()

# 绘制大括号
ax.text(0.5, 0.5, '{', fontsize=30, ha='center', va='center', rotation=0)

# 设置坐标轴
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')  # 隐藏坐标轴

plt.show()
