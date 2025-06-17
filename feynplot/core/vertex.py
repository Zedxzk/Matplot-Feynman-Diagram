from enum import Enum
import numpy as np
from typing import Dict, Any, Optional

class VertexType(Enum):
    ELECTROMAGNETIC = "electromagnetic"
    STRONG = "strong"
    WEAK = "weak"
    HIGHER_ORDER = "higher_order"

class Vertex:
    def __init__(self, x, y, vertex_type=VertexType.ELECTROMAGNETIC, label="", 
                 coupling_constant=1.0, symmetry_factor=1, 
                 label_offset=(0.15, 0.15), 
                 
                 # --- 结构化顶点相关参数 ---
                 is_structured: bool = False, # 是否是结构化顶点
                 structured_radius: float = 0.5, # 结构化顶点的半径
                 structured_facecolor: str = 'lightgray', # 结构化顶点的填充颜色
                 structured_edgecolor: str = 'black', # 结构化顶点的边框和阴影线颜色
                 structured_linewidth: float = 1.5, # 结构化顶点的边框线宽
                 structured_alpha: float = 1.0, # 结构化顶点的透明度
                 
                 # --- 阴影模式选择和默认hatch参数 ---
                 use_custom_hatch: bool = False, # 是否使用自定义阴影线 (True: 自定义, False: Matplotlib内置hatch)
                 hatch_pattern: Optional[str] = '/', # 仅当 use_custom_hatch 为 False 时生效

                 # --- 自定义阴影线参数 (仅当 use_custom_hatch 为 True 时生效) ---
                 custom_hatch_line_color: str = 'black',  # 自定义阴影线的颜色
                 custom_hatch_line_width: float = 0.5,    # 自定义阴影线的线宽
                 custom_hatch_line_angle_deg: float = 45, # 自定义阴影线的倾斜角度 (度)
                 custom_hatch_spacing_ratio: float = 0.1, # 自定义阴影线之间的间距 (相对于半径的比例)
                 # --- 结构化顶点参数结束 ---
                 
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
        self.process_type = "scattering"
        self.metadata = {}
        
        # 提取核心的 Matplotlib scatter 参数作为 Vertex 实例的属性 (用于非结构化顶点)
        self.size = kwargs.pop('s', 100) 
        self.color = kwargs.pop('c', 'blue') 
        self.marker = kwargs.pop('marker', 'o') 
        self.alpha = kwargs.pop('alpha', 1.0) 
        self.edgecolor = kwargs.pop('edgecolor', self.color) 
        self.linewidth = kwargs.pop('linewidth', 1.0) 
        self.zorder = kwargs.pop('zorder', 2) # 普通顶点的 Z 序

        # 标签相关参数
        self.label_size = kwargs.pop('fontsize', kwargs.pop('label_size', 12))
        self.label_color = kwargs.pop('label_color', kwargs.pop('labelcolor', 'black'))
        self.label_offset = np.array(label_offset) # 确保是 numpy 数组

        # 结构化顶点参数
        self.is_structured = is_structured
        self.structured_radius = structured_radius
        self.structured_facecolor = structured_facecolor
        self.structured_edgecolor = structured_edgecolor
        self.structured_linewidth = structured_linewidth
        self.structured_alpha = structured_alpha
        self.zorder_structured = self.zorder # 结构化顶点也使用 zorder

        # 阴影模式选择和参数
        self.use_custom_hatch = use_custom_hatch
        self.hatch_pattern = hatch_pattern # Matplotlib 内置 hatch
        self.custom_hatch_line_color = custom_hatch_line_color
        self.custom_hatch_line_width = custom_hatch_line_width
        self.custom_hatch_line_angle_deg = custom_hatch_line_angle_deg
        self.custom_hatch_spacing_ratio = custom_hatch_spacing_ratio
        
        # 将所有剩余的 kwargs 存储到 scatterConfig 中，主要用于非结构化顶点
        self.scatterConfig: Dict[str, Any] = kwargs 


    def position(self):
        return (self.x, self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __array__(self, dtype=None):
        return np.array([self.x, self.y], dtype=dtype)

    def get_scatter_properties(self) -> Dict[str, Any]:
        """
        返回适用于 Matplotlib scatter() 函数的绘图属性字典 (主要用于非结构化顶点)。
        """
        base_properties = {}
        base_properties.update(self.scatterConfig) # 额外的 kwargs
        base_properties['s'] = self.size 
        base_properties['c'] = self.color
        base_properties['marker'] = self.marker
        base_properties['alpha'] = self.alpha
        base_properties['edgecolor'] = self.edgecolor
        base_properties['linewidth'] = self.linewidth
        base_properties['zorder'] = self.zorder
        return base_properties

    def get_circle_properties(self) -> Dict[str, Any]:
        """
        返回适用于 Matplotlib Circle() 函数的绘图属性字典 (用于结构化顶点的主体圆圈)。
        当使用自定义阴影时，这个字典不包含 'hatch'。
        """
        props = {
            'radius': self.structured_radius,
            'facecolor': self.structured_facecolor,
            'edgecolor': self.structured_edgecolor,
            'linewidth': self.structured_linewidth,
            'alpha': self.structured_alpha,
            'zorder': self.zorder_structured 
        }
        # 只有在不使用自定义阴影时才添加内置 hatch
        if not self.use_custom_hatch:
            props['hatch'] = self.hatch_pattern
        return props

    def get_custom_hatch_properties(self) -> Dict[str, Any]:
        """
        返回用于自定义阴影线的属性字典。
        """
        return {
            'hatch_line_color': self.custom_hatch_line_color,
            'hatch_line_width': self.custom_hatch_line_width,
            'hatch_line_angle_deg': self.custom_hatch_line_angle_deg,
            'hatch_spacing_ratio': self.custom_hatch_spacing_ratio,
        }

    def get_label_properties(self) -> Dict[str, Any]:
        """
        返回适用于 Matplotlib text() 函数的标签样式字典。
        """
        return {
            'fontsize': self.label_size,
            'color': self.label_color,
            'ha': 'center', 
            'va': 'center' 
        }