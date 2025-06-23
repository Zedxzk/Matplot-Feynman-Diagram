# feynplot/core/vertex.py

from enum import Enum
import numpy as np
from typing import Dict, Any, Optional

# IMPORTANT: 为了避免顶层循环导入 feynplot.io.diagram_io，
# 我们将在 to_dict 和 from_dict 方法内部进行局部导入。

# --- VertexType 枚举 (保持不变) ---
class VertexType(Enum):
    ELECTROMAGNETIC = "electromagnetic"
    STRONG = "strong"
    WEAK = "weak"
    HIGHER_ORDER = "higher_order"
    GENERIC = "generic"

# --- Vertex 类 (init 和其他方法保持不变) ---
class Vertex:
    # 用于生成唯一ID的计数器
    _vertex_counter_global = 0

    def __init__(self, x, y, vertex_type=VertexType.ELECTROMAGNETIC, label="",
                 coupling_constant=1.0, symmetry_factor=1,
                 label_offset=(0.5, 0.0),
                 is_structured: bool = False,
                 structured_radius: float = 0.5,
                 structured_facecolor: str = 'lightgray',
                 structured_edgecolor: str = 'black',
                 structured_linewidth: float = 1.5,
                 structured_alpha: float = 1.0,
                 use_custom_hatch: bool = False,
                 hatch_pattern: Optional[str] = '/',
                 custom_hatch_line_color: str = 'black',
                 custom_hatch_line_width: float = 0.5,
                 custom_hatch_line_angle_deg: float = 45,
                 custom_hatch_spacing_ratio: float = 0.1,
                 **kwargs):

        self.x = x
        self.y = y
        self.vertex_type = vertex_type
        self.label = label
        self.coupling_constant = coupling_constant
        self.symmetry_factor = symmetry_factor
        self.particle_types = []
        self.momenta = []
        self.time_order = 0
        self.metadata = {}
        self.hidden_vertex = False
        self.hidden_label  = False
        self.highlighted_vertex = False

        self.id = kwargs.pop('id', f"vertex_{Vertex._vertex_counter_global}")
        if self.id.startswith("vertex_"):
            Vertex._vertex_counter_global += 1

        self.is_selected: bool = False

        self.size = kwargs.pop('s', 100)
        self.color = kwargs.pop('c', 'black')
        self.marker = kwargs.pop('marker', 'o')
        self.alpha = kwargs.pop('alpha', 1.0)
        self.edgecolor = kwargs.pop('edgecolor', self.color)
        self.linewidth = kwargs.pop('linewidth', 1.0)
        self.zorder = kwargs.pop('zorder', 2)

        self.label_size = kwargs.pop('fontsize', kwargs.pop('label_size', 30))
        self.label_color = kwargs.pop('label_color', kwargs.pop('labelcolor', 'black'))
        self.label_offset = np.array(label_offset)

        self.is_structured = is_structured
        self.structured_radius = structured_radius
        self.structured_facecolor = structured_facecolor
        self.structured_edgecolor = structured_edgecolor
        self.structured_linewidth = structured_linewidth
        self.structured_alpha = structured_alpha
        self.zorder_structured = self.zorder

        self.use_custom_hatch = use_custom_hatch
        self.hatch_pattern = hatch_pattern
        self.custom_hatch_line_color = custom_hatch_line_color
        self.custom_hatch_line_width = custom_hatch_line_width
        self.custom_hatch_line_angle_deg = custom_hatch_line_angle_deg
        self.custom_hatch_spacing_ratio = custom_hatch_spacing_ratio

        # self.scatterConfig: Dict[str, Any] = kwargs

    def position(self):
        return (self.x, self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __array__(self, dtype=None):
        return np.array([self.x, self.y], dtype=dtype)

    def get_scatter_properties(self) -> Dict[str, Any]:
        base_properties = {}
        base_properties['s'] = self.size
        base_properties['c'] = self.color
        base_properties['marker'] = self.marker
        base_properties['alpha'] = self.alpha
        base_properties['edgecolor'] = self.edgecolor
        base_properties['linewidth'] = self.linewidth
        base_properties['zorder'] = self.zorder
        # base_properties.update(self.scatterConfig)
        return base_properties

    def get_circle_properties(self) -> Dict[str, Any]:
        props = {
            'radius': self.structured_radius,
            'facecolor': self.structured_facecolor,
            'edgecolor': self.structured_edgecolor,
            'linewidth': self.structured_linewidth,
            'alpha': self.structured_alpha,
            'zorder': self.zorder_structured
        }
        if not self.use_custom_hatch:
            props['hatch'] = self.hatch_pattern
        return props

    def get_custom_hatch_properties(self) -> Dict[str, Any]:
        return {
            'hatch_line_color': self.custom_hatch_line_color,
            'hatch_line_width': self.custom_hatch_line_width,
            'hatch_line_angle_deg': self.custom_hatch_line_angle_deg,
            'hatch_spacing_ratio': self.custom_hatch_spacing_ratio,
        }

    def get_label_properties(self) -> Dict[str, Any]:
        return {
            'fontsize': self.label_size,
            'color': self.label_color,
            'ha': 'center',
            'va': 'center'
        }

    def update_properties(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'label_offset' and isinstance(value, (list, tuple)):
                    setattr(self, key, np.array(value))
                elif key == 'vertex_type' and isinstance(value, str):
                    try:
                        setattr(self, key, VertexType[value.upper()])
                    except KeyError:
                        print(f"警告: 无效的 VertexType '{value}'。属性 '{key}' 未更新。")
                elif key in self.scatterConfig:
                    self.scatterConfig[key] = value
                else:
                    setattr(self, key, value)
            elif key in ['s', 'c', 'marker', 'alpha', 'edgecolor', 'linewidth', 'zorder']:
                if key == 's': self.size = value
                elif key == 'c': self.color = value
                elif key == 'marker': self.marker = value
                elif key == 'alpha': self.alpha = value
                elif key == 'edgecolor': self.edgecolor = value
                elif key == 'linewidth': self.linewidth = value
                elif key == 'zorder': self.zorder = value
            elif key in ['fontsize', 'label_size', 'label_color', 'labelcolor']:
                if key in ['fontsize', 'label_size']: self.label_size = value
                elif key in ['label_color', 'labelcolor']: self.label_color = value
            elif key in ['is_structured', 'structured_radius', 'structured_facecolor',
                          'structured_edgecolor', 'structured_linewidth', 'structured_alpha',
                          'use_custom_hatch', 'hatch_pattern', 'custom_hatch_line_color',
                          'custom_hatch_line_width', 'custom_hatch_line_angle_deg',
                          'custom_hatch_spacing_ratio']:
                setattr(self, key, value)
            else:
                self.metadata[key] = value

    def hide(self):
        self.hidden_vertex = True

    def show(self):
        self.hidden_vertex = False

    def hide_label(self):
        self.hidden_label = True

    def show_label(self):
        self.hidden_label = False

    def to_dict(self) -> Dict[str, Any]:
        """
        将 Vertex 实例序列化为一个字典，通过调用外部 IO 辅助函数实现。
        此方法不直接返回字典，而是将自身传递给序列化函数。
        """
        # 局部导入 feynplot.io.diagram_io，以避免顶层循环依赖
        from feynplot.io.diagram_io import _vertex_to_dict

        # 调用外部辅助函数进行序列化，并返回其结果
        return _vertex_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vertex':
        """
        从字典数据创建 Vertex 实例，通过调用外部 IO 辅助函数实现。
        这是一个类方法，可以直接通过 Vertex.from_dict(data) 调用。
        """
        # 局部导入 feynplot.io.diagram_io，以避免顶层循环依赖
        from feynplot.io.diagram_io import _vertex_from_dict

        # 调用外部辅助函数进行反序列化，并返回 Vertex 实例
        return _vertex_from_dict(data)