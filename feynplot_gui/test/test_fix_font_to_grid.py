import matplotlib.pyplot as plt

def draw_text_with_data_width(ax, x, y, text, width_in_data_units):
    fig = ax.figure
    renderer = fig.canvas.get_renderer()

    # 坐标范围
    x0, x1 = ax.get_xlim()
    fig_width_inch = fig.get_size_inches()[0]
    dpi = fig.get_dpi()

    # 数据单位 -> 像素
    pixels_per_data_unit = (fig_width_inch * dpi) / (x1 - x0)
    desired_width_pixels = width_in_data_units * pixels_per_data_unit

    # 先用默认大小画一个临时文字，测量像素宽度
    tmp_text = ax.text(x, y, text, fontsize=10, va='center')
    fig.canvas.draw()  # 渲染一次，获取 renderer
    bbox = tmp_text.get_window_extent(renderer=renderer)
    text_width_pixels = bbox.width

    # 按比例调整 fontsize
    scale_factor = desired_width_pixels / text_width_pixels
    tmp_text.set_fontsize(10 * scale_factor)

    return tmp_text


# ====== 绘图 ======
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# 场景 1：坐标 0~10
ax1 = axes[0]
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 5)
draw_text_with_data_width(ax1, 1, 4, "width=1 unit", 1)
draw_text_with_data_width(ax1, 1, 3, "width=2 units", 2)
draw_text_with_data_width(ax1, 1, 2, "width=3 units", 3)
# 辅助线
ax1.plot([1, 2], [4, 4], 'r-', lw=2)
ax1.plot([1, 3], [3, 3], 'g-', lw=2)
ax1.plot([1, 4], [2, 2], 'b-', lw=2)
ax1.set_title("x range 0~10")

# 场景 2：坐标 0~5（放大 2 倍）
ax2 = axes[1]
ax2.set_xlim(0, 5)
ax2.set_ylim(0, 5)
draw_text_with_data_width(ax2, 1, 4, "width=1 unit", 1)
draw_text_with_data_width(ax2, 1, 3, "width=2 units", 2)
draw_text_with_data_width(ax2, 1, 2, "width=3 units", 3)
# 辅助线
ax2.plot([1, 2], [4, 4], 'r-', lw=2)
ax2.plot([1, 3], [3, 3], 'g-', lw=2)
ax2.plot([1, 4], [2, 2], 'b-', lw=2)
ax2.set_title("x range 0~5")

plt.tight_layout()
plt.show()
