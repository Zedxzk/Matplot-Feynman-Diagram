import matplotlib.pyplot as plt

fig, ax = plt.subplots()

# 使用 \left 和 \right 来实现可变大小的大括号
# Mathtext 支持这种语法
ax.text(0.5, 0.5, r'$\left\{ \frac{a}{b} \right\}$', ha='center', va='center', fontsize=20)

ax.set_title("Using mathtext with \left and \right")
plt.show()