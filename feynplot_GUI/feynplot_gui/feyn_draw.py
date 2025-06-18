# gui/feyn_draw.py
from PySide6.QtGui import QPainter # 尽管不再直接使用QPainter，但保留以防万一或作为未来扩展点

# 导入你的 Matplotlib 后端渲染器
from feynplot.drawing.renderer import MatplotlibBackend 
from feynplot.core.diagram import FeynmanDiagram

# 在 feyn_draw 模块级别实例化 MatplotlibBackend
# 这样每次 draw_feyn 被调用时，都可以重用同一个 MatplotlibBackend 实例，
# 从而在同一个 Matplotlib Figure 上进行更新和重绘。
_matplotlib_backend = MatplotlibBackend()

def draw_feyn(painter: QPainter, diagram: FeynmanDiagram, view_scale: float):
    """
    通过 MatplotlibBackend 渲染 Feynman 图。
    注意：这里的 painter 和 view_scale 参数对于 MatplotlibBackend 来说是多余的，
    因为 MatplotlibBackend 有自己的绘图上下文。它们被保留以便与 Controller 接口兼容，
    但 MatplotlibBackend 将直接使用其内部的 fig/ax 来渲染。
    """
    # MatplotlibBackend 直接从其内部的 fig 和 ax 进行绘图，
    # 它需要访问图的顶点和线列表。
    _matplotlib_backend.render(diagram.vertices, diagram.lines)

    # 关键步骤：获取 Matplotlib 图形并将其渲染到 PyQt 的 QPainter 上。
    # 我们将把这个逻辑移到 CanvasWidget 中，因为 CanvasWidget 才是真正的绘图表面。
    # 这里我们只负责调用 MatplotlibBackend 的 render 方法，
    # 让它更新其内部的 Matplotlib Figure。
    pass # 实际上，这个函数本身不会绘制到 QPainter，它会触发 MatplotlibBackend 的绘图