import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np

from feynplot.core.diagram import FeynmanDiagram
# Ensure FermionLine is imported along with other line types
from feynplot.core.line import GluonLine, PhotonLine, WPlusLine, WMinusLine, ZBosonLine, FermionLine, AntiFermionLine 
from feynplot.core.vertex import Vertex, VertexType 
from feynplot.core.style import set_style_from_dict
from feynplot.drawing.renderer import FeynmanDiagramCanvas

plt.style.use(hep.style.CMS)
# plt.rcParams['figure.figsize'] = (12, 8) 
plt.rcParams['font.family'] = "Times New Roman"
plt.rcParams['text.usetex'] = True

set_style_from_dict({
    "font.size": 12,
    "axes.linewidth": 1.2
})

# Create the Feynman diagram object
diagram = FeynmanDiagram()

# Add regular vertices
v1 = diagram.add_vertex(0, 0, label='A')
v2 = diagram.add_vertex(5, 5, label='B')
v3 = diagram.add_vertex(10, 5, label='C')
v4 = diagram.add_vertex(5, 0, label='D')
v5 = diagram.add_vertex(10, 0, label='E')
v6 = diagram.add_vertex(2.5, 7.5, label='F')
v7 = diagram.add_vertex(7.5, -2.5, label='G')

# --- 构建结构化顶点 ---

# v_struct1: 现在使用自定义的粗斜线阴影
v_struct1 = diagram.add_vertex(
    -2, 2,
    label=r'Struct$_1$',
    is_structured=True,
    use_custom_hatch=True, # <--- 启用自定义阴影
    structured_radius=0.8,
    structured_facecolor='lightgray',
    structured_edgecolor='black',
    structured_linewidth=2.0,
    label_offset=(0, 0.9),

    # 自定义阴影参数
    custom_hatch_line_color='darkred',      # 红色阴影线
    custom_hatch_line_width=1.0,            # 较粗的阴影线
    custom_hatch_line_angle_deg=60,         # 倾斜 60 度
    custom_hatch_spacing_ratio=0.2         # 较密的间距
)

# v_struct2: 依然使用 Matplotlib 内置的 'x' 阴影模式进行对比
v_struct2 = diagram.add_vertex(
    13, 2, # 注意：我将X坐标也改成了13，为了和之前的讨论一致，确保它显示
    label=r'Struct$_2$',
    is_structured=True,
    structured_radius=1.0,
    structured_facecolor='lightgoldenrodyellow', # 淡黄色填充
    structured_edgecolor='darkorange',
    mpl_hatch_pattern='//', # <--- 这里改成 '///' 让阴影更密集
    structured_linewidth=1.5,
    structured_alpha=1.0, # 稍微透明
    label_offset=(0, -1.5)
)

# v_struct3: 现在使用自定义的细斜线阴影
v_struct3 = diagram.add_vertex(
    5, -5,
    label=r'Compos.\,P',
    is_structured=True,
    use_custom_hatch=True, # <--- 启用自定义阴影
    structured_radius=0.7,
    structured_facecolor='lavender', # 淡紫色填充
    structured_edgecolor='darkblue',
    structured_linewidth=1.0,
    label_offset=(0.8, 0.0),
    vertex_type=VertexType.HIGHER_ORDER, 

    # 自定义阴影参数
    custom_hatch_line_color='blue',         # 蓝色阴影线
    custom_hatch_line_width=0.4,            # 较细的阴影线
    custom_hatch_line_angle_deg=-30,        # 倾斜 -30 度
    custom_hatch_spacing_ratio=0.12         # 标准间距
)

# Add gluon lines
gluon = GluonLine(
    label='g',
    amplitude=0.4,
    label_offset=[0.1, -0.1],
    linewidth=2.0,
    color='purple',
    label_size=25,
    alpha=0.2,
    n_cycles=8,
)
gluon2 = GluonLine(
    label='g',
    amplitude=0.4,
    bezier_offset=0.5,
    label_offset=[0.1, -0.1],
    linewidth=2.0,
    color='black',
    label_size=16,
    alpha=0.2,
    n_cycles=8,
)
gluon2.angleOut = 90
gluon2.angleIn = 150

diagram.add_line(v1, v2, gluon)
diagram.add_line(v1, v2, gluon2)

# Add photon lines
photon1 = PhotonLine(
    label=r'$\gamma_1$',
    label_size=20,
    amplitude=0.3,
    wavelength=1.0,
    label_offset=[0, 0.4],
    linewidth=1.5,
    color='black',
    linestyle='-',
    alpha=0.8,
    arrow=True,
    initial_phase=0,
    final_phase=0,
)
photon2 = PhotonLine(
    label=r'$\gamma_2$',
    label_size=40,
    amplitude=0.55,
    wavelength=0.5,
    label_offset=[-0.0, -0.9],
    linewidth=1.0,
    color='green',
    linestyle='-',
    alpha=0.7,
    arrow=True,
    initial_phase=0,
    final_phase=180,
)
diagram.add_line(v2, v3, photon1)
diagram.add_line(v1, v3, photon2)

# Add W⁺ line
w_plus = WPlusLine(
    amplitude=0.2,
    wavelength=0.6,
    label=r'$W^+$',
    label_size=18,
    label_offset=[0.2, 0.3],
    linewidth=2.0,
    color='blue',
    arrow=True,
    alpha=0.9,
)
diagram.add_line(v1, v4, w_plus)

# Add W⁻ line
w_minus = WMinusLine(
    amplitude=0.2,
    wavelength=0.6,
    label=r'$W^-$',
    label_size=18,
    label_offset=[0.2, 0.3],
    linewidth=2.0,
    color='red',
    arrow=True,
    alpha=0.9,
)
diagram.add_line(v2, v4, w_minus)

# Add Z⁰ line
z_boson = ZBosonLine(
    amplitude=0.2,
    wavelength=0.6,
    label=r'$Z^0$',
    label_size=18,
    label_offset=[0.2, 0.3],
    linewidth=2.0,
    color='gray',
    arrow=True,
    alpha=0.9,
    angleIn = -50,
    angleOut = 50,
    bezier_offset = 0.5,
)
print("Z_boson.bezier_offset =", z_boson.bezier_offset)
diagram.add_line(v3, v5, z_boson)

# --- Add Fermion Lines ---

# A simple fermion line
fermion1 = FermionLine(
    label=r'$e^-$',
    label_size=16,
    label_offset=[0.1, -0.2],
    linewidth=1.5,
    color='darkgreen',
    arrow=True,
    bezier_offset=0.2, # Slight curve
    angleOut=45,
    angleIn=135,
)
diagram.add_line(v4, v5, fermion1)

# Another fermion line with different styling
fermion2 = FermionLine(
    label=r'$u$',
    label_size=16,
    label_offset=[-0.2, 0.1],
    linewidth=1.8,
    color='darkblue',
    arrow=True,
    bezier_offset=0.6, # More pronounced curve
)
diagram.add_line(v5, v7, fermion2)

# Incoming fermion line
fermion3 = FermionLine(
    label=r'$\bar{\nu}_e$',
    label_size=16,
    label_offset=[0, -0.3],
    linewidth=1.5,
    color='brown',
    arrow=True,
    bezier_offset=0.1,
)
diagram.add_line(v6, v1, fermion3)

# Outgoing fermion line
fermion4 = FermionLine(
    label=r'$\mu^+$',
    label_size=16,
    label_offset=[0, 0.3],
    linewidth=1.5,
    color='orange',
    arrow=True,
    bezier_offset=0.1,
)
diagram.add_line(v3, v6, fermion4)

# --- 添加连接结构化顶点的线条 ---
line_to_struct1 = PhotonLine(label=r'$\gamma$', color='purple', bezier_offset=0.3)
diagram.add_line(v1, v_struct1, line_to_struct1)

line_from_struct1 = FermionLine(label=r'$q$', color='navy', arrow=True, arrow_position=0.7, bezier_offset=0.4)
diagram.add_line(v_struct1, v2, line_from_struct1)

line_to_struct2 = WMinusLine(label=r'$W^-$', color='crimson', arrow=True, arrow_reversed=True)
diagram.add_line(v3, v_struct2, line_to_struct2) # 指向结构化顶点

line_from_struct2 = AntiFermionLine(label=r'$\bar{q}$', color='teal', arrow_filled=True, arrow_size=15.0)
diagram.add_line(v_struct2, v5, line_from_struct2) # 从结构化顶点发出反费米子

line_from_struct3_1 = GluonLine(label=r'$g_1$', color='darkred', n_cycles=6)
diagram.add_line(v_struct3, v4, line_from_struct3_1)

line_from_struct3_2 = FermionLine(label=r'$\tau$', color='darkmagenta', arrow=True, arrow_line_width=2.5, bezier_offset=0.2, angleIn=220, angleOut=300)
diagram.add_line(v_struct3, v7, line_from_struct3_2)


backend = FeynmanDiagramCanvas()
backend.render(diagram.vertices, diagram.lines)

# 调整X和Y轴范围以更好地显示所有顶点
ax = backend.ax
ax.set_xlim(-2.9, 14.1)
ax.set_ylim(-6, 8.5)
# plt.tight_layout()

backend.savefig("feynman_diagram_with_custom_structured_vertices.png", dpi=400,  bbox_inches='tight', pad_inches=0,)
backend.savefig("feynman_diagram_with_custom_structured_vertices.pdf", bbox_inches='tight', pad_inches=0,)

backend.show()

print("示例图已保存为 feynman_diagram_with_custom_structured_vertices.png 和 .pdf")