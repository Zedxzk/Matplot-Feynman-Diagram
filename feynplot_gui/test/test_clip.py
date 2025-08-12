import matplotlib.pyplot as plt

# 创建一个图表和轴
plt.rcParams['font.family'] = 'SimHei'
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# 在轴的外部添加文本，默认情况下会显示
ax.text(9, 6, '这个文本在轴外面', fontsize=12)

# 在轴的内部添加文本，并设置 clip_on=True
# 尝试将文本放在轴的外面，它将不会被显示
ax.text(9, 5, '这个文本也会被裁剪', fontsize=12, clip_on=True)

plt.show()