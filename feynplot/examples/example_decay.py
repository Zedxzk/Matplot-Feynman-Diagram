from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.line import GluonLine
# from feynplot.core.particle import GluonLine
from feynplot.core.style import set_style_from_dict
from feynplot.drawing.renderer import MatplotlibBackend

# 可选：自定义 matplotlib 风格
set_style_from_dict({
    "font.size": 12,
    "axes.linewidth": 1.2
})

# 创建图
diagram = FeynmanDiagram()

# 添加两个顶点：起点和终点
v1 = diagram.add_vertex(0, 0)
v2 = diagram.add_vertex(5, 0)

# 添加胶子线连接这两个点
gluon = GluonLine(label='g')
diagram.add_line(v1, v2, gluon)

# 渲染图像
backend = MatplotlibBackend()
backend.render(diagram.vertices, diagram.lines)

# 保存图像（记得在 MatplotlibBackend 里实现 savefig）
backend.savefig("gluon_line_example.png")
