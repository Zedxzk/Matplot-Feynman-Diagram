import matplotlib.pyplot as plt
import matplotlib

# 设置全局字体（可分别为中英文设置）
matplotlib.rcParams['font.family'] = 'Times New Roman'  # 英文字体
matplotlib.rcParams['font.sans-serif'] = ['SimSun']     # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False        # 解决负号显示问题
matplotlib.rcParams['mathtext.fontset'] = 'stix'      # 解决负号显示问题

# 创建画布
fig, ax = plt.subplots()

# 绘制中文和希腊字母 gamma（两种字体）
ax.text(0.1, 0.8, '中文伽马 (SimSun)', fontname='SimSun', fontsize=25)
ax.text(0.1, 0.6, r'$\gamma$ (Times New Roman)', fontname='Times New Roman', fontsize=25)
ax.text(0.1, 0.4, r'$\gamma$ (SimSun)', fontname='SimSun', fontsize=25)
matplotlib.rcParams['mathtext.fontset'] = 'cm'      # 解决负号显示问题
ax.text(0.1, 0.2, r'$\gamma (Times New Roman)$', fontsize=25)

# 设置坐标轴不可见
ax.axis('off')

plt.title('字体示例：中文与Times New Roman', fontsize=16)
plt.show()
