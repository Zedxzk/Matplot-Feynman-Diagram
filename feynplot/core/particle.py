from feynplot.core.line import Line


class ParticleLine:
    def __init__(self, ptype='fermion', label='', style=None):
        self.ptype = ptype
        self.label = label
        self.style = style or {}

class FermionLine(Line):
    def __init__(self, label='', arrow=False, **kwargs):
        super().__init__(style='fermion', label=label, arrow=arrow, **kwargs)

class BosonLine(ParticleLine):
    def __init__(self, label='', style=None):
        super().__init__('boson', label, style)


# from feynplot.core.line import Line

# class FermionLine(Line):
#     """费米子线（实线）"""
#     def __init__(self, label='', arrow=True, **kwargs):
#         super().__init__(style='fermion', label=label, arrow=arrow, **kwargs)

class PhotonLine(Line):
    """光子线（波浪线）"""
    def __init__(self, label='', arrow=False, **kwargs):
        # 确保 kwargs 中不包含 style 参数
        kwargs.pop('style', None)
        super().__init__(style='photon', label=label, arrow=arrow, **kwargs)

class GluonLine(Line):
    """胶子线（螺旋线）"""
    def __init__(self, label='', arrow=False, **kwargs):
        super().__init__(style='gluon', label=label, arrow=arrow, **kwargs)

class WZLine(Line):
    """W/Z 玻色子线（折线）"""
    def __init__(self, label='', arrow=False, **kwargs):
        super().__init__(style='wz', label=label, arrow=arrow, **kwargs)

