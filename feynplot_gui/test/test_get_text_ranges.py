import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 创建图形和坐标轴
fig, ax = plt.subplots(figsize=(10, 8))

# 方法1: 使用Text对象的get_window_extent()方法
text1 = ax.text(0.2, 0.8, 'Hello World!', fontsize=16, transform=ax.transAxes)
# 需要先渲染才能获取准确的边界框
fig.canvas.draw()
# 获取窗口坐标系中的边界框
bbox_window = text1.get_window_extent()
# 转换为数据坐标系
bbox_data = bbox_window.transformed(ax.transData.inverted())
print(f"方法1 - 数据坐标系边界框: {bbox_data}")

# 方法2: 直接获取数据坐标系中的边界框
bbox_data_direct = text1.get_window_extent().transformed(ax.transData.inverted())
print(f"方法2 - 直接获取: x0={bbox_data_direct.x0:.3f}, y0={bbox_data_direct.y0:.3f}")
print(f"       宽度={bbox_data_direct.width:.3f}, 高度={bbox_data_direct.height:.3f}")

# 方法3: 使用renderer获取更精确的边界框
renderer = fig.canvas.get_renderer()
text2 = ax.text(0.2, 0.6, 'Another Text', fontsize=20)
bbox_renderer = text2.get_window_extent(renderer=renderer)
bbox_data2 = bbox_renderer.transformed(ax.transData.inverted())

# 方法4: 创建文字时就设置bbox参数来可视化边界框
text3 = ax.text(0.2, 0.4, 'Text with visible bbox', fontsize=14,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))

# 方法5: 手动绘制边界框矩形
text4 = ax.text(0.2, 0.2, 'Manual bbox visualization', fontsize=12)
fig.canvas.draw()  # 确保渲染完成
bbox4 = text4.get_window_extent().transformed(ax.transData.inverted())

# 绘制手动边界框
rect = patches.Rectangle((bbox4.x0, bbox4.y0), bbox4.width, bbox4.height,
                        linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
ax.add_patch(rect)

# 方法6: 获取文字的四个角点坐标
def get_text_corners(text_obj, ax):
    """获取文字的四个角点坐标"""
    bbox = text_obj.get_window_extent().transformed(ax.transData.inverted())
    corners = {
        'bottom_left': (bbox.x0, bbox.y0),
        'bottom_right': (bbox.x1, bbox.y0),
        'top_left': (bbox.x0, bbox.y1),
        'top_right': (bbox.x1, bbox.y1)
    }
    return corners, bbox

corners, bbox = get_text_corners(text4, ax)
print(f"方法6 - 四个角点:")
for corner_name, (x, y) in corners.items():
    print(f"  {corner_name}: ({x:.3f}, {y:.3f})")

# 方法7: 实时获取边界框的函数
def get_text_bbox_info(text_obj, fig, ax):
    """获取文字边界框的完整信息"""
    # 确保渲染
    fig.canvas.draw()
    
    # 获取窗口坐标系边界框
    bbox_window = text_obj.get_window_extent()
    # 转换为数据坐标系
    bbox_data = bbox_window.transformed(ax.transData.inverted())
    
    info = {
        'x_min': bbox_data.x0,
        'y_min': bbox_data.y0,
        'x_max': bbox_data.x1,
        'y_max': bbox_data.y1,
        'width': bbox_data.width,
        'height': bbox_data.height,
        'center_x': bbox_data.x0 + bbox_data.width / 2,
        'center_y': bbox_data.y0 + bbox_data.height / 2
    }
    return info

# 测试实时获取函数
text5 = ax.text(0.6, 0.5, 'Test Text for Info', fontsize=18, color='blue')
info = get_text_bbox_info(text5, fig, ax)
print(f"\n方法7 - 完整信息:")
for key, value in info.items():
    print(f"  {key}: {value:.3f}")

# 设置坐标轴
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('Text Bounding Box Examples')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 方法8: 处理动态变化的文字边界框
def update_text_bbox(text_obj, new_text, fig, ax):
    """更新文字内容并返回新的边界框"""
    text_obj.set_text(new_text)
    fig.canvas.draw()
    return text_obj.get_window_extent().transformed(ax.transData.inverted())

# 方法9: 批量获取多个文字对象的边界框
def get_multiple_text_bbox(text_objects, fig, ax):
    """批量获取多个文字对象的边界框"""
    fig.canvas.draw()
    bboxes = []
    for text_obj in text_objects:
        bbox = text_obj.get_window_extent().transformed(ax.transData.inverted())
        bboxes.append(bbox)
    return bboxes