import math
import arrow
import numpy as np
from typing import Dict, Any, Optional

class LineStyle:
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

class Line:
    # 修改 __init__ 的签名
    def __init__(self, style: LineStyle = LineStyle.FERMION, label: str = '', 
                 label_offset=(0.0, -0.5), 
                 # plot_config 和 label_config 将直接作为字典传入，或通过 kwargs 额外提供
                 line_plot_config: Optional[Dict[str, Any]] = None, 
                 label_plot_config: Optional[Dict[str, Any]] = None,
                 angleIn=None,angleOut=None, bezier_offset = 0.3,
                 **kwargs):
        
        self.style = style
        self.label = label
        self.label_offset = np.array(label_offset) # 确保是 numpy 数组
        # self.arrow = arrow
        self.v_start = None
        self.v_end = None
        self.angleOut = angleOut # 直接命名为 angleOut
        self.angleIn = angleIn  # 直接命名为 angleIn
        self.bezier_offset = bezier_offset # 默认值

        # 初始化 line_plot_config 和 label_plot_config 字典
        # 将用户传入的字典作为起点，如果为 None 则初始化为空字典
        self.linePlotConfig = line_plot_config if line_plot_config is not None else {}
        self.labelPlotConfig = label_plot_config if label_plot_config is not None else {}

        # --- 从 kwargs 中提取常见的 Matplotlib 参数，并将其归类到对应的配置字典中 ---
        # 对于线条绘图参数 (linePlotConfig)
        self.linePlotConfig['linewidth'] = kwargs.pop('linewidth', self.linePlotConfig.get('linewidth', 1.0))
        self.linePlotConfig['color'] = kwargs.pop('color', self.linePlotConfig.get('color', None)) # None 意味着可能由 LineStyle 决定
        self.linePlotConfig['linestyle'] = kwargs.pop('linestyle', self.linePlotConfig.get('linestyle', None))
        self.linePlotConfig['alpha'] = kwargs.pop('alpha', self.linePlotConfig.get('alpha', 1.0))
        self.linePlotConfig['zorder'] = kwargs.pop('zorder', self.linePlotConfig.get('zorder', 1)) # 线条通常在顶点下方

        # 支持别名 (例如 'lw' for 'linewidth', 'c' for 'color', 'ls' for 'linestyle')
        if 'lw' in kwargs: self.linePlotConfig['linewidth'] = kwargs.pop('lw')
        if 'c' in kwargs: self.linePlotConfig['color'] = kwargs.pop('c')
        if 'ls' in kwargs: self.linePlotConfig['linestyle'] = kwargs.pop('ls')


        # 对于标签绘图参数 (labelPlotConfig)
        self.labelPlotConfig['fontsize'] = kwargs.pop('fontsize', self.labelPlotConfig.get('fontsize', 10))
        self.labelPlotConfig['color'] = kwargs.pop('label_color', self.labelPlotConfig.get('color', 'black')) # 优先使用 label_color，否则使用 color
        self.labelPlotConfig['ha'] = kwargs.pop('ha', self.labelPlotConfig.get('ha', 'center')) # Horizontal alignment
        self.labelPlotConfig['va'] = kwargs.pop('va', self.labelPlotConfig.get('va', 'center')) # Vertical alignment

        # 支持别名 (例如 'label_size' for 'fontsize', 'labelcolor' for 'color')
        if 'label_size' in kwargs: self.labelPlotConfig['fontsize'] = kwargs.pop('label_size')
        if 'labelcolor' in kwargs: self.labelPlotConfig['color'] = kwargs.pop('labelcolor')


        # 将所有未被明确提取的剩余 kwargs 存储，以防用户传入其他 Matplotlib 参数或自定义参数
        # 此时 kwargs 应该只包含那些没有被 pop() 掉的参数
        self.other_options = kwargs 
        # 可以选择将这些也合并到 linePlotConfig 或 labelPlotConfig 中，
        # 但如果它们是通用参数，最好单独存储或在 get_plot_properties 中统一处理。
        # 这里为了演示，我们假设只将明确的参数归类。
        # 如果你希望所有剩余的 kwargs 都默认应用于线条，可以这样：
        # self.linePlotConfig.update(kwargs) 
        # 但这可能会导致一些非线条参数混入，所以慎用。



    def set_vertices(self, v_start, v_end):
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")

        self.v_start = v_start
        self.v_end = v_end

        if self._angleOut is None: # 使用 _angleOut 访问内部变量，避免触发 property setter
            self._angleOut = self._calc_angle(v_start, v_end)
        if self._angleIn is None: # 使用 _angleIn 访问内部变量
            self._angleIn = self._calc_angle(v_end, v_start)

    @staticmethod
    def _calc_angle(p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        angle_rad = math.atan2(dy, dx)
        return math.degrees(angle_rad)

    @property
    def angleOut(self):
        return self._angleOut

    @angleOut.setter
    def angleOut(self, value):
        self._angleOut = value

    @property
    def angleIn(self):
        return self._angleIn

    @angleIn.setter
    def angleIn(self, value):
        self._angleIn = value

    def get_coords(self):
        if self.v_start is None or self.v_end is None:
            raise ValueError("v_start 和 v_end 必须先设置")
        return (self.v_start.x, self.v_start.y), (self.v_end.x, self.v_end.y)

    def get_plot_properties(self) -> Dict[str, Any]:
        """
        返回适用于 Matplotlib plot() 函数的样式字典。
        优先级：LineStyle 默认值 < 用户传入的 line_plot_config 字典 < kwargs (最终传入)
        """
        # 默认样式，基于 LineStyle
        style_properties_defaults = {
            LineStyle.FERMION: {'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.PHOTON: {'linestyle': '-', 'color': 'blue', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.GLUON:   {'linestyle': '-', 'color': 'red', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.WZ:      {'linestyle': '-.', 'color': 'green', 'linewidth': 1.0, 'zorder': 1},
        }
        
        # 获取 LineStyle 对应的基础样式，如果 style 不在 defaults 中，则使用通用默认值
        final_properties = style_properties_defaults.get(self.style, {
            'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 1
        }).copy() # 使用 copy() 避免修改原始字典

        # 合并 self.linePlotConfig 中存储的参数。这些是用户在实例化时明确传入的。
        # 这会覆盖 LineStyle 的默认值。
        final_properties.update(self.linePlotConfig)
        
        # 此时，final_properties 包含了 LineStyle 默认值和用户在 line_plot_config
        # 或 kwargs 中直接设置的行样式。

        return final_properties

    def get_label_properties(self) -> Dict[str, Any]:
        """
        返回适用于 Matplotlib text() 函数的标签样式字典。
        优先级：默认值 < 用户传入的 label_plot_config 字典 < kwargs (最终传入)
        """
        # 标签默认样式，如果用户没有指定，则使用这些
        default_label_properties = {
            'fontsize': 10,
            'color': 'black',
            'ha': 'center',
            'va': 'center'
        }
        
        # 合并 self.labelPlotConfig 中存储的参数。
        # 这会覆盖 default_label_properties。
        final_label_properties = default_label_properties.copy()
        final_label_properties.update(self.labelPlotConfig)
        
        return final_label_properties

# -------------------------
# 中间类 - 移除对 label 的处理，直接传递 kwargs
# -------------------------

class FermionLine(Line):
    def __init__(
        self,
        arrow=True,          # 是否绘制箭头
        arrow_filled=False,  # 箭头是否实心 (True: 实心, False: 空心)
        arrow_position=None,  # 箭头沿线的相对位置 (0.0: 起点, 0.5: 中间, 1.0: 终点)
        arrow_size=10.0,      # 箭头大小的缩放因子 (1.0 为默认大小)
        arrow_line_width=None, # 箭头线条的宽度 (None 表示使用线条的 linewidth)
        arrow_reversed=True,# 箭头方向是否反转 (True: 反转, False: 正常方向)
        **kwargs
    ):
        super().__init__(style=LineStyle.FERMION, **kwargs)
        self.arrow = arrow
        self.arrow_filled = arrow_filled
        self.arrow_position = arrow_position
        self.arrow_size = arrow_size
        self.arrow_line_width = arrow_line_width # 新增：箭头线宽
        self.arrow_reversed = arrow_reversed


class AntiFermionLine(FermionLine):
    def __init__(
        self,
        # AntiFermionLine 的 arrow_reversed 默认设置为 True
        arrow_reversed=True, 
        **kwargs
    ):
        # 调用父类 FermionLine 的构造函数
        # arrow_reversed=True 会覆盖 FermionLine 中的默认值
        super().__init__(arrow_reversed=arrow_reversed, **kwargs)
        # 你可以在这里设置反费米子特有的其他默认值，例如颜色或标签
        # self.line_plot_config.setdefault('color', 'red') 
        # self.label = self.label if self.label else r'$\bar{f}$' # 默认标签


class BosonLine(Line):
    def __init__(self, style=LineStyle.PHOTON, arrow=False, **kwargs):
        super().__init__(style=style, arrow=arrow, **kwargs)

# -------------------------
# 费米子示例 - 在最具体的子类中处理默认 label
# -------------------------

class ElectronLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'e⁻')
        super().__init__(label=label, **kwargs)

class PositronLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'e⁺')
        super().__init__(label=label, **kwargs)

class MuonLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'μ⁻')
        super().__init__(label=label, **kwargs)

class TauLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'τ⁻')
        super().__init__(label=label, **kwargs)

class NeutrinoLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'ν')
        super().__init__(label=label, **kwargs)

# -------------------------
# 夸克示例 (与费米子示例类似，都在具体子类中处理 label)
# -------------------------

class UpQuarkLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'u')
        super().__init__(label=label, **kwargs)

class DownQuarkLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'd')
        super().__init__(label=label, **kwargs)

class CharmQuarkLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'c')
        super().__init__(label=label, **kwargs)

class StrangeQuarkLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 's')
        super().__init__(label=label, **kwargs)

class TopQuarkLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 't')
        super().__init__(label=label, **kwargs)

class BottomQuarkLine(FermionLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'b')
        super().__init__(label=label, **kwargs)

# -------------------------
# 玻色子示例 - 修正 GluonLine 和其他具体玻色子
# -------------------------

class PhotonLine(BosonLine):
    def __init__(self, amplitude=0.1, wavelength=0.5, initial_phase=0, final_phase=0, **kwargs):
        """
        初始化一个光子线。

        参数:
            amplitude (float): 波浪的幅度。
            wavelength (float): 波浪的（标称）波长。
            initial_phase (int): 波浪在起点处的相位（度）。仅接受 0 或 180。
            final_phase (int): 波浪在终点处的相位（度）。仅接受 0 或 180。
            **kwargs: 传递给基类 BosonLine 的其他参数。
        """
        label = kwargs.pop('label', r'\gamma')
        super().__init__(label=label, style=LineStyle.PHOTON, **kwargs)
        
        self.amplitude = amplitude
        self.wavelength = wavelength

        # # 验证并设置初始和最终相位
        # if initial_phase not in [0, 180]:
        #     raise ValueError("initial_phase 只能是 0 或 180 度。")
        # if final_phase not in [0, 180]:
        #     raise ValueError("final_phase 只能是 0 或 180 度。")

        self.initial_phase = initial_phase
        self.final_phase = final_phase

class GluonLine(BosonLine):
    def __init__(self, amplitude=0.1, wavelength=0.2, n_cycles=16, bezier_offset=0.3, **kwargs):
        label = kwargs.pop('label', 'g')
        super().__init__(label=label, style=LineStyle.GLUON, **kwargs)
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.n_cycles = n_cycles
        self.bezier_offset = bezier_offset

    def get_plot_path(self):
        # 假设 feynplot.core.gluon_methods 存在且可用
        from feynplot.core.gluon_methods import generate_gluon_helix
        if self.v_start is None or self.v_end is None:
            raise ValueError("v_start 和 v_end 必须先设置")
        return generate_gluon_helix(self)


class WPlusLine(BosonLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', r'W^{+}')
        super().__init__(label=label, style=LineStyle.WZ, **kwargs)

class WMinusLine(BosonLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', r'W^{-}')
        super().__init__(label=label, style=LineStyle.WZ, **kwargs)

class ZBosonLine(BosonLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', r'Z^{0}')
        super().__init__(label=label, style=LineStyle.WZ, **kwargs)

class HiggsLine(BosonLine):
    def __init__(self, **kwargs):
        label = kwargs.pop('label', 'H')
        super().__init__(label=label, style=LineStyle.WZ, **kwargs)