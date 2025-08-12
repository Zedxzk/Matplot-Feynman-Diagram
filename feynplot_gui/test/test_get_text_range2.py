import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import numpy as np

# 创建图形
fig, ax = plt.subplots(figsize=(12, 8))

# 演示1: 绘制前后的差异
print("=== 演示1: 绘制前后获取边界框的差异 ===")
text1 = ax.text(0.1, 0.8, 'Test Text', fontsize=16)

# 绘制前尝试获取（通常会得到错误或不准确的结果）
try:
    bbox_before = text1.get_window_extent()
    print(f"绘制前边界框: {bbox_before}")
    print(f"绘制前数据坐标: {bbox_before.transformed(ax.transData.inverted())}")
except Exception as e:
    print(f"绘制前获取失败: {e}")

# 绘制后获取
fig.canvas.draw()
bbox_after = text1.get_window_extent()
bbox_data = bbox_after.transformed(ax.transData.inverted())
print(f"绘制后边界框: {bbox_after}")
print(f"绘制后数据坐标: 宽度={bbox_data.width:.4f}, 高度={bbox_data.height:.4f}")

# 演示2: 为什么需要渲染？
print("\n=== 演示2: 渲染的必要性 ===")
print("matplotlib需要以下信息来计算准确的边界框:")
print("- 字体渲染信息（字符实际像素大小）")
print("- 当前DPI设置")
print("- 坐标轴的变换矩阵") 
print("- 图形的实际尺寸")

# 演示3: 解决方案 - 使用FontProperties估算
print("\n=== 演示3: 绘制前的估算方法 ===")

def estimate_text_size(text, fontsize, ax):
    """在绘制前估算文字大小（近似方法）"""
    # 方法1: 基于字符数的粗略估算
    char_count = len(text)
    # 经验值：每个字符大约占字体大小的0.6倍宽度
    estimated_width = char_count * fontsize * 0.0006  # 转换为数据坐标
    estimated_height = fontsize * 0.0008  # 转换为数据坐标
    
    return estimated_width, estimated_height

# 方法2: 使用matplotlib的文字测量工具
def get_text_dimensions_before_draw(text, fontsize, fig):
    """在绘制前获取文字尺寸的更精确方法"""
    # 创建一个临时的renderer
    temp_fig = plt.figure(figsize=(1, 1))
    temp_ax = temp_fig.add_subplot(111)
    temp_text = temp_ax.text(0, 0, text, fontsize=fontsize)
    
    # 强制渲染这个临时图形
    temp_fig.canvas.draw()
    
    # 获取边界框
    bbox = temp_text.get_window_extent()
    
    # 清理临时图形
    plt.close(temp_fig)
    
    # 返回像素尺寸
    return bbox.width, bbox.height

# 测试估算方法
test_text = "Hello World Test"
test_fontsize = 14

estimated_w, estimated_h = estimate_text_size(test_text, test_fontsize, ax)
print(f"粗略估算: 宽度={estimated_w:.4f}, 高度={estimated_h:.4f}")

try:
    accurate_w, accurate_h = get_text_dimensions_before_draw(test_text, test_fontsize, fig)
    print(f"精确预测: 宽度={accurate_w:.1f}px, 高度={accurate_h:.1f}px")
except:
    print("精确预测方法在某些环境下可能不可用")

# 演示4: 实际绘制并比较
text2 = ax.text(0.1, 0.6, test_text, fontsize=test_fontsize, color='blue')
fig.canvas.draw()
actual_bbox = text2.get_window_extent().transformed(ax.transData.inverted())
print(f"实际测量: 宽度={actual_bbox.width:.4f}, 高度={actual_bbox.height:.4f}")

# 演示5: 动态获取边界框的最佳实践
print("\n=== 演示5: 最佳实践 ===")

class TextWithBBox:
    """带边界框管理的文字类"""
    def __init__(self, ax, x, y, text, **kwargs):
        self.ax = ax
        self.text_obj = ax.text(x, y, text, **kwargs)
        self.bbox = None
        self.is_drawn = False
    
    def update_bbox(self, fig):
        """更新边界框"""
        if not self.is_drawn:
            fig.canvas.draw()
            self.is_drawn = True
        self.bbox = self.text_obj.get_window_extent().transformed(
            self.ax.transData.inverted()
        )
        return self.bbox
    
    def get_bbox(self, fig):
        """获取边界框，如果未渲染则先渲染"""
        if self.bbox is None or not self.is_drawn:
            return self.update_bbox(fig)
        return self.bbox
    
    def set_text(self, new_text, fig):
        """更新文字内容并重新计算边界框"""
        self.text_obj.set_text(new_text)
        self.is_drawn = False
        return self.update_bbox(fig)

# 使用示例
smart_text = TextWithBBox(ax, 0.1, 0.4, "Smart Text Object", fontsize=12, color='green')
bbox = smart_text.get_bbox(fig)
print(f"智能文字对象边界框: 宽度={bbox.width:.4f}, 高度={bbox.height:.4f}")

# 演示6: 批量处理的优化方法
print("\n=== 演示6: 批量处理优化 ===")

def batch_create_texts_with_bbox(ax, fig, text_data_list):
    """批量创建文字并一次性获取所有边界框"""
    text_objects = []
    
    # 首先创建所有文字对象
    for x, y, text, kwargs in text_data_list:
        text_obj = ax.text(x, y, text, **kwargs)
        text_objects.append(text_obj)
    
    # 一次性渲染
    fig.canvas.draw()
    
    # 批量获取边界框
    bboxes = []
    for text_obj in text_objects:
        bbox = text_obj.get_window_extent().transformed(ax.transData.inverted())
        bboxes.append(bbox)
    
    return text_objects, bboxes

# 测试批量处理
text_data = [
    (0.5, 0.8, "Text 1", {'fontsize': 10, 'color': 'red'}),
    (0.5, 0.6, "Text 2", {'fontsize': 12, 'color': 'blue'}),
    (0.5, 0.4, "Text 3", {'fontsize': 14, 'color': 'green'})
]

batch_texts, batch_bboxes = batch_create_texts_with_bbox(ax, fig, text_data)
print("批量处理结果:")
for i, bbox in enumerate(batch_bboxes):
    print(f"  文字{i+1}: 宽度={bbox.width:.4f}, 高度={bbox.height:.4f}")

# 设置图形
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('Text BBox Timing Examples')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n=== 总结 ===")
print("1. 必须在 fig.canvas.draw() 后才能获取准确边界框")
print("2. 可以使用估算方法在绘制前获得近似尺寸")
print("3. 对于动态文字，建议封装成类管理边界框状态")
print("4. 批量处理时，可以先创建所有文字，然后一次性渲染和获取边界框")