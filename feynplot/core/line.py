import math
import numpy as np

class LineStyle:
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

class Line:
    def __init__(self, style=LineStyle.FERMION, label='', arrow=False, **kwargs):
        self.style = style
        self.label = label # Line 类最终接收并设置 label
        self.arrow = arrow
        self.v_start = None
        self.v_end = None
        self.options = kwargs
        self._angleOut = None
        self._angleIn = None

    def set_vertices(self, v_start, v_end):
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")

        self.v_start = v_start
        self.v_end = v_end

        if self.angleOut is None:
            self.angleOut = self._calc_angle(v_start, v_end)
        if self.angleIn is None:
            self.angleIn = self._calc_angle(v_end, v_start)

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

    def get_style_properties(self):
        style_properties = {
            LineStyle.FERMION: {'linestyle': '-', 'color': 'black'},
            LineStyle.PHOTON: {'linestyle': '--', 'color': 'blue'},
            LineStyle.GLUON:  {'linestyle': '-',  'color': 'red'},
            LineStyle.WZ:     {'linestyle': '-.', 'color': 'green'},
        }
        return style_properties.get(self.style, {'linestyle': '-', 'color': 'black'})

    def get_plot_path(self):
        raise NotImplementedError("请在子类中实现 get_plot_path 方法")

# -------------------------
# 中间类 - 移除对 label 的处理，直接传递 kwargs
# -------------------------

class FermionLine(Line):
    def __init__(self, **kwargs):
        # FermionLine 应该只设置自己特有的属性或传递 style/arrow，
        # label 和其他 kwargs 都直接传给 Line
        super().__init__(style=LineStyle.FERMION, arrow=True, **kwargs)

class BosonLine(Line):
    def __init__(self, style=LineStyle.PHOTON, arrow=False, **kwargs):
        # BosonLine 也是如此
        super().__init__(style=style, arrow=arrow, **kwargs)

# -------------------------
# 费米子示例 - 在最具体的子类中处理默认 label
# -------------------------

class ElectronLine(FermionLine):
    def __init__(self, **kwargs):
        # 在这里从 kwargs 中弹出 label，并设置默认值
        label = kwargs.pop('label', 'e⁻')
        super().__init__(label=label, **kwargs) # 将处理好的 label 显式传给父类

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
    def __init__(self, **kwargs):
        label = kwargs.pop('label', r'\gamma')
        super().__init__(label=label, style=LineStyle.PHOTON, **kwargs)

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