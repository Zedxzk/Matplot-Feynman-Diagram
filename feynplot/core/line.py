import math
import numpy as np
from typing import Dict, Any, Optional
from debug_utils import cout

import debug_utils
# from dataclasses import dataclass, field # 如果你需要dataclass，请保留，目前看来你没有用
# from feynplot.core.gluon_methods import generate_gluon_helix # 假设这个导入在运行时需要

# --- LineStyle 枚举 ---
class LineStyle:
    STRAIGHT = 'straight' # 新增：通用的直线样式
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

# --- Line 类 ---
class Line:
    # 用于生成唯一ID的计数器
    _line_counter_global = 0

class Line:
    _line_counter_global = 0

    def __init__(self, v_start, v_end,
                #  style: LineStyle = LineStyle.STRAIGHT, # <-- 保持 style 作为显式参数
                 label: str = '',
                 label_offset=(0.0, -0.5),
                 line_plot_config: Optional[Dict[str, Any]] = None,
                 label_plot_config: Optional[Dict[str, Any]] = None,
                 angleIn=None, angleOut=None, bezier_offset=0.3,
                 **kwargs):

        # 确保 v_start 和 v_end 被正确赋值
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")
        
        self.v_start = v_start
        self.v_end = v_end

        # --- 修正 style 处理逻辑 ---
        # 获取 kwargs 中可能存在的 style 字符串
        kwargs_style_str = kwargs.pop('style', None) 
        
        # # 确定最终要使用的 style 值（枚举成员或字符串）
        # final_style_val = None
        # if kwargs_style_str is not None:
        #     # 如果 kwargs 提供了 style 字符串，则尝试将其转换为枚举成员
        #     try:
        #         final_style_val = getattr(LineStyle, kwargs_style_str.upper())
        #     except AttributeError:
        #         print(f"警告: 无法识别的线条样式 '{kwargs_style_str}'。将使用默认或显式设置。")
        #         final_style_val = style # 如果转换失败，则回退到显式 style 参数
        # else:
        #     final_style_val = style # 如果 kwargs 中没有 style，就直接使用显式 style 参数

        # # 最后赋值给 self.style，确保它是一个 LineStyle 枚举成员
        # # 如果 final_style_val 已经是 LineStyle 枚举成员，就直接赋值
        # # 如果是字符串，就尝试转换（这种情况应该通过上面 kwargs_style_str 的处理来避免）
        # if isinstance(final_style_val, LineStyle):
        #     self.style = final_style_val
        # elif isinstance(final_style_val, str):
        #     # 这通常不应该发生，但作为双重保障
        #     try:
        #         self.style = getattr(LineStyle, final_style_val.upper())
        #     except AttributeError:
        #         print(f"警告: 最终 style 值 '{final_style_val}' 无法转换为 LineStyle 枚举。请检查。")
        #         self.style = LineStyle.STRAIGHT # 回退到安全默认值
        # else:
        #     self.style = LineStyle.STRAIGHT # 任何其他异常情况

        self.label = label
        self.label_offset = np.array(label_offset)
        
        self._angleOut = angleOut 
        self._angleIn = angleIn
        
        self.bezier_offset = bezier_offset

        self.id = kwargs.pop('id', f"line_{Line._line_counter_global}")
        if self.id.startswith("line_"):
            Line._line_counter_global += 1

        self.linePlotConfig = line_plot_config if line_plot_config is not None else {}
        self.labelPlotConfig = label_plot_config if label_plot_config is not None else {}

        self.is_selected: bool = False 

        # 从 kwargs 中提取常见的 Matplotlib 参数，并将其归类到对应的配置字典中
        # 对于线条绘图参数 (linePlotConfig)
        self.linePlotConfig['linewidth'] = kwargs.pop('linewidth', self.linePlotConfig.get('linewidth', 1.0))
        self.linePlotConfig['color'] = kwargs.pop('color', self.linePlotConfig.get('color', 'black'))
        self.linePlotConfig['linestyle'] = kwargs.pop('linestyle', self.linePlotConfig.get('linestyle', None))
        self.linePlotConfig['alpha'] = kwargs.pop('alpha', self.linePlotConfig.get('alpha', 1.0))
        self.linePlotConfig['zorder'] = kwargs.pop('zorder', self.linePlotConfig.get('zorder', 1))

        # 支持别名 (例如 'lw' for 'linewidth', 'c' for 'color', 'ls' for 'linestyle')
        if 'lw' in kwargs: self.linePlotConfig['linewidth'] = kwargs.pop('lw')
        if 'c' in kwargs: self.linePlotConfig['color'] = kwargs.pop('c')
        if 'ls' in kwargs: self.linePlotConfig['linestyle'] = kwargs.pop('ls')

        # 对于标签绘图参数 (labelPlotConfig)
        self.labelPlotConfig['fontsize'] = kwargs.pop('fontsize', self.labelPlotConfig.get('fontsize', 10))
        self.labelPlotConfig['color'] = kwargs.pop('label_color', self.labelPlotConfig.get('color', 'black'))
        self.labelPlotConfig['ha'] = kwargs.pop('ha', self.labelPlotConfig.get('ha', 'center'))
        self.labelPlotConfig['va'] = kwargs.pop('va', self.labelPlotConfig.get('va', 'center'))

        # 支持别名 (例如 'label_size' for 'fontsize', 'labelcolor' for 'color')
        if 'label_size' in kwargs: self.labelPlotConfig['fontsize'] = kwargs.pop('label_size')
        if 'labelcolor' in kwargs: self.labelPlotConfig['color'] = kwargs.pop('labelcolor')

        # 将所有未被明确提取的剩余 kwargs 更新到 linePlotConfig 中
        # 这是一种通用处理未知绘图参数的方式，如果有冲突，用户传入的kwargs会覆盖默认和LineStyle预设
        self.linePlotConfig.update(kwargs)
        # --- 在这里添加新的调试打印语句 ---
        # 如果 angleIn/out 没传，则自动计算
        if self._angleOut is None or self._angleIn is None:
            self.set_vertices(v_start, v_end)
        cout(f"DEBUG(Line_init): ID='{self.id}', linePlotConfig地址={id(self.linePlotConfig)}, 初始颜色='{self.linePlotConfig.get('color', '未设置')}'")
        # --- 调试打印结束 ---

    def set_vertices(self, v_start, v_end):
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")

        self.v_start = v_start
        self.v_end = v_end

        # 仅在 _angleOut 或 _angleIn 未明确设置时才计算
        if self._angleOut is None:
            self._angleOut = self._calc_angle(v_start, v_end)
        if self._angleIn is None:
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
            LineStyle.STRAIGHT: {'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.FERMION: {'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.PHOTON: {'linestyle': '-', 'color': 'blue', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.GLUON:   {'linestyle': '-', 'color': 'red', 'linewidth': 1.0, 'zorder': 1},
            LineStyle.WZ:      {'linestyle': '-.', 'color': 'green', 'linewidth': 1.0, 'zorder': 1},
        }
        
        # 获取 LineStyle 对应的基础样式，如果 style 不在 defaults 中，则使用通用默认值
        final_properties = style_properties_defaults.get(LineStyle.STRAIGHT)
        # .get(self.style, {
        #     'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 1
        # }).copy()

        # 合并 self.linePlotConfig 中存储的参数。这会覆盖 LineStyle 的默认值。
        final_properties.update(self.linePlotConfig)
        
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
        final_label_properties = default_label_properties.copy()
        final_label_properties.update(self.labelPlotConfig)
        
        return final_label_properties

    # --- 新增的 update_properties 方法，用于动态更新属性 ---
    def update_properties(self, **kwargs):
        """
        根据传入的关键字参数更新线条的属性。
        这包括直接属性、linePlotConfig 和 labelPlotConfig 中的参数。
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and not key.startswith('_'): # 避免修改私有属性
                # 特殊处理 numpy 数组 (例如 label_offset)
                if key == 'label_offset' and isinstance(value, (list, tuple)):
                    setattr(self, key, np.array(value))
                # 特殊处理 LineStyle 枚举
                elif key == 'style' and isinstance(value, str):
                    try:
                        setattr(self, key, LineStyle[value.upper()])
                    except KeyError:
                        print(f"警告: 无效的 LineStyle '{value}'。属性 '{key}' 未更新。")
                # 显式处理 linePlotConfig 和 labelPlotConfig 的字典更新
                elif key == 'linePlotConfig' and isinstance(value, dict):
                    self.linePlotConfig.update(value)
                elif key == 'labelPlotConfig' and isinstance(value, dict):
                    self.labelPlotConfig.update(value)
                else:
                    setattr(self, key, value)
            # 如果不是直接属性，检查是否为 linePlotConfig 或 labelPlotConfig 中的常见参数
            elif key in self.linePlotConfig:
                self.linePlotConfig[key] = value
            elif key in self.labelPlotConfig:
                self.labelPlotConfig[key] = value
            # 处理别名，并将其映射到对应的配置字典中
            elif key == 'lw': self.linePlotConfig['linewidth'] = value
            elif key == 'c': self.linePlotConfig['color'] = value
            elif key == 'ls': self.linePlotConfig['linestyle'] = value
            elif key == 'label_size': self.labelPlotConfig['fontsize'] = value
            elif key == 'labelcolor': self.labelPlotConfig['color'] = value
            else:
                # 对于未知参数，默认添加到 linePlotConfig
                self.linePlotConfig[key] = value
                # print(f"警告: 属性 '{key}' 未直接处理，已存储在 linePlotConfig 中。") # 警告太多可以关闭

# --- 子类 (根据你的代码，它们现在不需要额外的修改，因为 is_selected 在基类中) ---

# --- 修正 FermionLine 类 ---
class FermionLine(Line):
    def __init__(
        self, v_start, v_end, # <-- 必须有 v_start, v_end
        arrow=True, # <-- 重新将 arrow 作为 FermionLine 的显式参数
        arrow_filled=False,
        arrow_position: Optional[float] = 0.5,
        arrow_size=10.0,
        arrow_line_width=None,
        arrow_reversed=False, 
        **kwargs # <-- 接收其他通用参数，传递给 Line 基类
    ):
        # 将 v_start, v_end 和其他通用 kwargs 传递给父类
        super().__init__(v_start, v_end, style=LineStyle.FERMION, **kwargs)
        # FermionLine 自身管理箭头的属性
        self.arrow = arrow
        self.arrow_filled = arrow_filled
        self.arrow_position = arrow_position
        self.arrow_size = arrow_size
        self.arrow_line_width = arrow_line_width
        self.arrow_reversed = arrow_reversed



class AntiFermionLine(FermionLine):
    def __init__(
        self,
        arrow_reversed=True, # 反费米子线默认箭头方向反转
        **kwargs
    ):
        super().__init__(arrow_reversed=arrow_reversed, **kwargs)

class BosonLine(Line):
    def __init__(self, v_start, v_end, **kwargs): # <-- Correctly accepts v_start, v_end
        # PROBLEM (if not fixed): This super() call also needs v_start and v_end
        super().__init__( v_start=v_start, v_end=v_end, **kwargs) # <--- If this doesn't pass v_start, v_end, it's also a problem

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
    def __init__(self, v_start, v_end, amplitude=0.1, wavelength=0.5, initial_phase=0, final_phase=0, **kwargs): # <-- Correctly accepts v_start, v_end
        label = kwargs.pop('label', r'\gamma')
        # PROBLEM: You're NOT passing v_start and v_end to super().__init__ here!
        super().__init__(label=label, v_start=v_start, v_end=v_end, **kwargs) # <--- This is the exact line causing the error!
        self.amplitude = amplitude
        self.wavelength = wavelength
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