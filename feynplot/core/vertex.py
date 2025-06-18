from enum import Enum
import numpy as np
from typing import Dict, Any, Optional

# --- VertexType 枚举 ---
class VertexType(Enum):
    ELECTROMAGNETIC = "electromagnetic"
    STRONG = "strong"
    WEAK = "weak"
    HIGHER_ORDER = "higher_order"
    # 新增一个通用类型，例如 GENERIC
    GENERIC = "generic" # <-- 在这里添加这一行！

# --- Vertex 类 ---
class Vertex:
    # 用于生成唯一ID的计数器
    _vertex_counter_global = 0

    def __init__(self, x, y, vertex_type=VertexType.ELECTROMAGNETIC, label="",
                 coupling_constant=1.0, symmetry_factor=1,
                 label_offset=(0.15, 0.15),

                 # --- 结构化顶点相关参数 ---
                 is_structured: bool = False,
                 structured_radius: float = 0.5,
                 structured_facecolor: str = 'lightgray',
                 structured_edgecolor: str = 'black',
                 structured_linewidth: float = 1.5,
                 structured_alpha: float = 1.0,

                 # --- 阴影模式选择和默认hatch参数 ---
                 use_custom_hatch: bool = False,
                 hatch_pattern: Optional[str] = '/',

                 # --- 自定义阴影线参数 (仅当 use_custom_hatch 为 True 时生效) ---
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

        # 从 kwargs 中提取 'id'，如果不存在则生成新ID
        self.id = kwargs.pop('id', f"vertex_{Vertex._vertex_counter_global}")
        if self.id.startswith("vertex_"): # 只有当ID是自动生成时才递增计数器
            Vertex._vertex_counter_global += 1

        # --- 新增属性：用于高亮显示 ---
        self.is_selected: bool = False # <--- 在这里添加这一行！

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
        self.hatch_pattern = hatch_pattern
        self.custom_hatch_line_color = custom_hatch_line_color
        self.custom_hatch_line_width = custom_hatch_line_width
        self.custom_hatch_line_angle_deg = custom_hatch_line_angle_deg
        self.custom_hatch_spacing_ratio = custom_hatch_spacing_ratio
        
        # 将所有剩余的 kwargs 存储到 scatterConfig 中，主要用于非结构化顶点
        # 这是为了确保所有未明确处理的 kwargs 都能传递给 Matplotlib 的 scatter 函数
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
        # 确保明确定义的属性覆盖通过 kwargs 传递的默认值
        base_properties['s'] = self.size
        base_properties['c'] = self.color
        base_properties['marker'] = self.marker
        base_properties['alpha'] = self.alpha
        base_properties['edgecolor'] = self.edgecolor
        base_properties['linewidth'] = self.linewidth
        base_properties['zorder'] = self.zorder
        # 最后，合并实例化时传入的剩余 kwargs (scatterConfig)
        base_properties.update(self.scatterConfig)
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

    def update_properties(self, **kwargs):
        """
        根据提供的关键字参数更新顶点的属性。

        Args:
            **kwargs: 关键字参数，键是属性名，值是新值。
                      示例: x=10.0, y=5.0, label="Updated Vertex"
        """
        for key, value in kwargs.items():
            # 优先更新直接属性
            if hasattr(self, key):
                # 特殊处理 numpy 数组 (例如 label_offset)
                if key == 'label_offset' and isinstance(value, (list, tuple)):
                    setattr(self, key, np.array(value))
                # 特殊处理 VertexType 枚举
                elif key == 'vertex_type' and isinstance(value, str):
                    try:
                        setattr(self, key, VertexType[value.upper()])
                    except KeyError:
                        print(f"警告: 无效的 VertexType '{value}'。属性 '{key}' 未更新。")
                # 更新到 scatterConfig 的参数
                elif key in self.scatterConfig:
                    self.scatterConfig[key] = value
                else:
                    setattr(self, key, value)
            # 如果不是直接属性，也不是 scatterConfig 中的键，则尝试作为 Matplotlib scatter 参数处理
            # 这里的逻辑可以根据你的具体需求进行调整。
            # 如果希望所有未知参数都进入 metadata，可以只保留 else 分支。
            elif key in ['s', 'c', 'marker', 'alpha', 'edgecolor', 'linewidth', 'zorder']:
                # 更新已知的 scatter 参数
                if key == 's': self.size = value
                elif key == 'c': self.color = value
                elif key == 'marker': self.marker = value
                elif key == 'alpha': self.alpha = value
                elif key == 'edgecolor': self.edgecolor = value
                elif key == 'linewidth': self.linewidth = value
                elif key == 'zorder': self.zorder = value
            elif key in ['fontsize', 'label_size', 'label_color', 'labelcolor']:
                # 更新标签参数
                if key in ['fontsize', 'label_size']: self.label_size = value
                elif key in ['label_color', 'labelcolor']: self.label_color = value
            elif key in ['is_structured', 'structured_radius', 'structured_facecolor',
                          'structured_edgecolor', 'structured_linewidth', 'structured_alpha',
                          'use_custom_hatch', 'hatch_pattern', 'custom_hatch_line_color',
                          'custom_hatch_line_width', 'custom_hatch_line_angle_deg',
                          'custom_hatch_spacing_ratio']:
                # 更新结构化顶点或阴影参数
                setattr(self, key, value)
            else:
                # 否则，存储到 metadata
                self.metadata[key] = value
                # print(f"警告: 属性 '{key}' 未直接处理，已存储在 metadata 中。") # 如果警告太多可以关闭