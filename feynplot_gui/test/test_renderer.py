import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# 绘制一个不可见的文本，颜色为 'none'
# 文本依然存在于图中，可以用于获取其边界
invisible_text = ax.text(5, 5, '这是一个不可见的文本', color='none')

# 绘制一个可见的文本
ax.text(5, 6, '这是一个可见的文本', color='black')

# 获取不可见文本的边界框
# 这一步需要先进行渲染
fig.canvas.draw()
bbox = invisible_text.get_window_extent()
print(f"Invisible：{bbox}")

plt.show()