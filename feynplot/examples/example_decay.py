from feynplot.core.diagram import FeynmanDiagram
from feynplot.core.particle import FermionLine, PhotonLine, GluonLine, WZLine
from feynplot.core.style import set_style_from_dict
from feynplot.core.vertex import Vertex
from feynplot.drawing.renderer import MatplotlibBackend

# 可选：自定义 matplotlib 风格
set_style_from_dict({
    "font.size": 12,
    "axes.linewidth": 1.2
})

# 创建图
diagram = FeynmanDiagram()

# 添加顶点
v_in1 = diagram.add_vertex(0, 1)    # e⁻
v_in2 = diagram.add_vertex(0, -1)   # e⁺
v_out1 = diagram.add_vertex(2, 1)   # μ⁻
v_out2 = diagram.add_vertex(2, -1)  # μ⁺
v_mid = diagram.add_vertex(1, 0)    # Z / γ 中间顶点

# 添加粒子线
diagram.add_line(v_in1, v_mid, FermionLine(label='e⁻', arrow=True))
diagram.add_line(v_in2, v_mid, FermionLine(label='e⁺', arrow=True))
diagram.add_line(v_mid, v_out1, FermionLine(label='μ⁻', arrow=True))
diagram.add_line(v_mid, v_out2, FermionLine(label='μ⁺', arrow=True))

# 添加中间传播子（Z/γ）
diagram.add_line(v_mid, v_mid, PhotonLine(label='Z/γ', style='photon'))

# 渲染图像（默认使用 matplotlib）
backend = MatplotlibBackend()
diagram.render()
backend.savefig("feynman_diagram.png")