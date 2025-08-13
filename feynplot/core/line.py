from ast import List
import math
from matplotlib.pyplot import get_plot_commands
import numpy as np
from typing import Dict, Any, Optional, Tuple
from feynplot_gui.debug_utils import cout

import enum 

# --- LineStyle Enum ---
class LineStyle(enum.Enum): 
    STRAIGHT = 'straight'
    FERMION = 'fermion'
    PHOTON = 'photon'
    GLUON = 'gluon'
    WZ = 'wz'

# --- Line Class ---
class Line:
    # Counter for generating unique IDs
    _line_counter_global = 1

    def __init__(self, v_start, v_end,
                 label: str = '',
                 label_offset=(0.3, -0.3),
                 angleIn=None, angleOut=None, bezier_offset=0.3,
                 # Direct line plotting attributes (formerly in linePlotConfig)
                 linewidth: float = 1.0,
                 color: str = 'black',
                 linestyle: Optional[str] = '-', # Default for STRAIGHT line style
                 alpha: float = 1.0,
                 zorder: int = 5,
                 # Direct label plotting attributes (formerly in labelPlotConfig)
                 label_fontsize: int = 30, # Renamed to avoid clash with `fontsize` kwarg
                 label_color: str = 'black', # Renamed to avoid clash with `color` kwarg
                 label_ha: str = 'left',
                 label_va: str = 'bottom',
                 hidden_label: bool = False,
                 # Style is now an internal property, not directly passed to super in subclasses
                 style: LineStyle = LineStyle.STRAIGHT, 
                 loop: bool = False,
                 **kwargs):
        # print(f"Line Initializing, kwargs: {kwargs}, loop: {loop}")  # Debugging output
        # Ensure v_start and v_end are correctly assigned
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")
        self.v_start = v_start
        self.v_end = v_end

        self.plot_points: List[Tuple[float, float]] = []


        # Line style (now a direct attribute)
        # Handle style conversion from string to enum if passed via kwargs
        if isinstance(style, str):
            try:
                self.style = getattr(LineStyle, style.upper())
            except KeyError:
                cout(f"WARNING: Invalid LineStyle string '{style}'. Defaulting to STRAIGHT.")
                self.style = LineStyle.STRAIGHT
        else:
            self.style = style

        self.label = label
        self.hidden_label = hidden_label
        self.label_offset = np.array(label_offset)
        
        self._angleOut = angleOut 
        self._angleIn = angleIn
        
        self.bezier_offset = bezier_offset

        self.id = kwargs.pop('id', f"l_{Line._line_counter_global}")
        if self.id.startswith("l_"):
            Line._line_counter_global += 1
        self.loop = loop
        self.a = None
        self.b = None
        self.angular_direction = None
        if self.loop:
            print(f"DEBUG(Line_init): Loop is enabled for line ID '{self.id}'")
            self.a = kwargs.pop('a', 1.0)  # 长半轴
            self.b = kwargs.pop('b', 1.0)  # 短半轴
            self.angular_direction = kwargs.pop('angular_direction', 90.0)  # 默认角度

        # --- Direct Line Plotting Attributes ---
        self.linewidth = kwargs.pop('linewidth', linewidth)
        self.color = kwargs.pop('color', color)
        # If linestyle wasn't explicitly passed, use the default based on the initial style.
        # This will be overridden by style_properties_defaults in get_plot_properties if no style.
        self.linestyle = kwargs.pop('linestyle', linestyle) 
        self.alpha = kwargs.pop('alpha', alpha)
        self.zorder = kwargs.pop('zorder', zorder)
        self.highlighted = kwargs.pop('highlighted', False)

        # Support aliases for line properties
        if 'lw' in kwargs: self.linewidth = kwargs.pop('lw')
        if 'c' in kwargs: self.color = kwargs.pop('c')
        if 'ls' in kwargs: self.linestyle = kwargs.pop('ls')

        # --- Direct Label Plotting Attributes ---
        self.label_fontsize = kwargs.pop('fontsize', label_fontsize) # 'fontsize' is a common kwarg in matplotlib
        self.label_color = kwargs.pop('label_color', label_color) # 'label_color' as explicit kwarg
        self.label_ha = kwargs.pop('ha', label_ha)
        self.label_va = kwargs.pop('va', label_va)

        # Support aliases for label properties
        if 'label_size' in kwargs: self.label_fontsize = kwargs.pop('label_size')
        if 'labelcolor' in kwargs: self.label_color = kwargs.pop('labelcolor')

        self.is_selected: bool = False 

        # Store any remaining kwargs directly as attributes, or raise warning if unexpected
        # For line, it's safer to store them in a dedicated 'metadata' or 'plot_config_extra'
        # dictionary if they aren't explicitly consumed, to avoid polluting the object's namespace.
        # For now, we'll follow the existing pattern if they are not predefined attributes.
        self.metadata = {}
        for key, value in kwargs.items():
            if not hasattr(self, key): # Only set if it's not already a predefined attribute
                # Check for other valid matplotlib.lines.Line2D properties
                # This is a heuristic; a more robust solution would be to match against
                # a known list of valid line plot properties.
                if key in ['dash_joinstyle', 'dash_capstyle', 'solid_joinstyle', 'solid_capstyle',
                           'drawstyle', 'fillstyle', 'markerfacecolor', 'markeredgecolor',
                           'markeredgewidth', 'markersize', 'marker', 'visible', 'picker',
                           'pickradius', 'antialiased', 'rasterized', 'url', 'snap']:
                    setattr(self, key, value)
                else:
                    self.metadata[key] = value # Store truly unknown kwargs in metadata
            # else:
                # If it already has the attribute, it was either set by init default
                # or through an alias. We don't want to re-set it if it was consumed.


        # If angleIn/out not provided, calculate them
        if self._angleOut is None or self._angleIn is None:
            self.set_vertices(v_start, v_end)
        
        print(f"DEBUG(Line_init): ID='{self.id}', Color='{self.color}', Linewidth='{self.linewidth}', Style='{self.style.name}'")
    def hide_label(self):
        self.hidden_label = True

    def show_label(self):
        self.hidden_label = False

    def set_vertices(self, v_start, v_end):
        # IMPORTANT: v_start and v_end must be Vertex-like objects, not their IDs.
        # Ensure we're assigning objects, not re-calculating from IDs.
        if not (hasattr(v_start, 'x') and hasattr(v_start, 'y')):
            raise TypeError("v_start 必须有 x 和 y 属性")
        if not (hasattr(v_end, 'x') and hasattr(v_end, 'y')):
            raise TypeError("v_end 必须有 x 和 y 属性")

        self.v_start = v_start
        self.v_end = v_end

        # Only calculate if _angleOut or _angleIn are not explicitly set
        if self._angleOut is None:
            self._angleOut = self._calc_angle(self.v_start, self.v_end)
        if self._angleIn is None:
            self._angleIn = self._calc_angle(self.v_end, self.v_start)

    def set_angles(self, v_start=None, v_end=None, angleOut=None, angleIn=None):
        # Update vertices if provided
        if v_start is not None:
            self.v_start = v_start
        if v_end is not None:
            self.v_end = v_end

        # Only update angles if explicitly provided or if vertices were updated and angles are None
        if angleOut is not None:
            self._angleOut = angleOut
        elif v_start is not None and v_end is not None: # Recalculate if vertices changed and angleOut not given
            self._angleOut = self._calc_angle(self.v_start, self.v_end)

        if angleIn is not None:
            self._angleIn = angleIn
        elif v_start is not None and v_end is not None: # Recalculate if vertices changed and angleIn not given
            self._angleIn = self._calc_angle(self.v_end, self.v_start)

    def reset_angles(self, angle_bias = 0):
        if self.v_start is not None and self.v_end is not None:
            self._angleOut = self._calc_angle(self.v_start, self.v_end) + angle_bias
            self._angleIn = self._calc_angle(self.v_end, self.v_start) - angle_bias
    
    def get_line_plot_points(self):
        if self.plot_points:
            return self.plot_points
    
    def set_plot_points(self, xs, ys):
        self.plot_points = [(x, y) for x, y in zip(xs, ys)]
        


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
        Returns a dictionary of plot properties suitable for Matplotlib plot() function.
        Prioritization: LineStyle defaults < instance attributes (final value)
        """
        # Default styles based on LineStyle
        style_properties_defaults = {
            LineStyle.STRAIGHT: {'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 5},
            LineStyle.FERMION: {'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 5},
            LineStyle.PHOTON: {'linestyle': '-', 'color': 'blue', 'linewidth': 1.0, 'zorder': 5},
            LineStyle.GLUON:   {'linestyle': '-', 'color': 'red', 'linewidth': 1.0, 'zorder': 5},
            LineStyle.WZ:      {'linestyle': '-.', 'color': 'green', 'linewidth': 1.0, 'zorder': 5},
        }
        
        # Start with properties based on the line's style
        # Use a copy to ensure we don't modify the default dicts directly
        final_properties = style_properties_defaults.get(self.style, {
            'linestyle': '-', 'color': 'black', 'linewidth': 1.0, 'zorder': 5
        }).copy()

        # Override with instance's direct attributes if they are not None
        # This ensures user-set values take precedence
        if self.linewidth is not None:
            final_properties['linewidth'] = self.linewidth
        if self.color is not None:
            final_properties['color'] = self.color
        if self.linestyle is not None:
            final_properties['linestyle'] = self.linestyle
        if self.alpha is not None:
            final_properties['alpha'] = self.alpha
        if self.zorder is not None:
            final_properties['zorder'] = self.zorder

        # Add any extra properties stored in metadata (if they are valid plot properties)
        # This could be more sophisticated by checking against a list of valid kwargs for Line2D
        # For now, we'll just add them to the properties
        final_properties.update(self.metadata)

        return final_properties
    
    def linePlotConfig(self):
        return self.get_plot_properties()

    def get_label_properties(self) -> Dict[str, Any]:
        """
        Returns a dictionary of label properties suitable for Matplotlib text() function.
        Prioritization: default values < instance attributes (final value)
        """
        # Label default styles
        default_label_properties = {
            'fontsize': 10,
            'color': 'black',
            'ha': 'left',   # <--- 修改这里
            'va': 'bottom'  # <--- 修改这里
        }
        
        # Start with defaults and then override with instance's direct attributes
        final_label_properties = default_label_properties.copy()

        if self.label_fontsize is not None:
            final_label_properties['fontsize'] = self.label_fontsize
        if self.label_color is not None:
            final_label_properties['color'] = self.label_color
        if self.label_ha is not None:
            final_label_properties['ha'] = self.label_ha
        if self.label_va is not None:
            final_label_properties['va'] = self.label_va
        
        return final_label_properties

    def labelPlotConfig(self):
        return self.get_label_properties()


    # --- New update_properties method for dynamic attribute updates ---
    def update_properties(self, **kwargs):
        """
        Updates the line's properties based on the provided keyword arguments.
        This includes direct attributes.
        """
        for key, value in kwargs.items():
            # Handle aliases first, mapping them to the actual attribute names
            if key == 'lw': 
                self.linewidth = value
            elif key == 'c': 
                self.color = value
            elif key == 'ls': 
                self.linestyle = value
            elif key == 'label_size': 
                self.label_fontsize = value
            elif key == 'labelcolor': 
                self.label_color = value
            # Explicitly handle style conversion
            elif key == 'style' and isinstance(value, (str, LineStyle)):
                if isinstance(value, str):
                    try:
                        self.style = LineStyle[value.upper()]
                    except KeyError:
                        cout(f"WARNING: Invalid LineStyle '{value}'. Property '{key}' not updated.")
                else: # Assume it's already a LineStyle enum
                    self.style = value
            # Handle specific attributes that might need type conversion
            elif key == 'label_offset' and isinstance(value, (list, tuple)):
                self.label_offset = np.array(value)
            # Directly set other attributes if they exist
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                # For any other unknown kwargs, store them in metadata
                self.metadata[key] = value
                # cout(f"WARNING: Attribute '{key}' not found or handled for Line.update_properties. Storing in metadata.")


    # --- to_dict and from_dict methods for serialization/deserialization ---
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the Line instance to a dictionary by calling an external IO helper.
        """
        # Local import to avoid top-level circular dependency
        from feynplot.io.diagram_io import _line_to_dict
        return _line_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], vertices_map: Dict[str, Any]) -> 'Line':
        """
        Creates a Line instance from dictionary data by calling an external IO helper.
        This is a class method, allowing creation via Line.from_dict(data, vertices_map).
        """
        # Local import to avoid top-level circular dependency
        from feynplot.io.diagram_io import _line_from_dict
        return _line_from_dict(data, vertices_map)

# --- Subclasses ---

class FermionLine(Line):
    def __init__(
        self, v_start, v_end, 
        arrow=True, 
        arrow_filled=False,
        arrow_position: Optional[float] = 0.5,
        arrow_size=10.0,
        arrow_line_width=None,
        arrow_reversed=False, 
        style: LineStyle = LineStyle.FERMION, # <--- 修正点：默认值在这里
        **kwargs
    ):
        # 从 kwargs 中取出 style，如果不存在则使用默认值
        style_to_pass = kwargs.pop('style', style)
        loop_to_pass = kwargs.pop('loop', False)  # 处理 loop 参数
        print(f"Passing Loop: {loop_to_pass} to FermionLine")
        super().__init__(v_start, v_end, style=style_to_pass, loop=loop_to_pass, **kwargs)
        # FermionLine manages its own arrow properties
        self.arrow = arrow
        self.arrow_filled = arrow_filled
        self.arrow_position = arrow_position
        self.arrow_size = arrow_size
        self.arrow_line_width = arrow_line_width
        self.arrow_reversed = arrow_reversed

class AntiFermionLine(FermionLine):
    def __init__(
        self, v_start, v_end, # Explicitly include v_start, v_end here
        arrow_reversed=True, # Anti-fermion line defaults to reversed arrow direction
        **kwargs
    ):
        # FermionLine 的 style 默认就是 FERMION，所以这里不需要再处理 style 参数
        # 除非 AntiFermionLine 需要一个完全不同的 LineStyle
        super().__init__(v_start=v_start, v_end=v_end, arrow_reversed=arrow_reversed, **kwargs)

class BosonLine(Line):
    def __init__(self, v_start, v_end, **kwargs):
        # BosonLine 是一个基类，通常不会直接实例化，所以它没有自己的特定 style 默认值
        # 它会继承 Line 的 STRAIGHT 默认 style
        super().__init__(v_start=v_start, v_end=v_end, **kwargs)

# -------------------------
# Fermion Examples - Handle default label in the most specific subclass
# -------------------------

class ElectronLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$e^{-}$') # Use LaTeX for proper rendering
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class PositronLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$e^{+}$') # Use LaTeX
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class MuonLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$\mu^{-}$') # Use LaTeX
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class TauLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$\tau^{-}$') # Use LaTeX
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class NeutrinoLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$\nu$') # Use LaTeX
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

# -------------------------
# Quark Examples (Similar to Fermion examples, handle label in specific subclass)
# -------------------------

class UpQuarkLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$u$')
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class DownQuarkLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$d$')
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class CharmQuarkLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$c$')
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class StrangeQuarkLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$s$')
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class TopQuarkLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$t$')
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

class BottomQuarkLine(FermionLine):
    def __init__(self, v_start, v_end, **kwargs):
        label = kwargs.pop('label', r'$b$')
        super().__init__(v_start=v_start, v_end=v_end, label=label, **kwargs)

# -------------------------
# Boson Examples - Corrected GluonLine and other specific bosons
# -------------------------

class PhotonLine(BosonLine):
    def __init__(self, v_start, v_end, amplitude=0.1, wavelength=0.5, initial_phase=0, final_phase=0, 
                 style: LineStyle = LineStyle.PHOTON, # <--- 修正点：默认值在这里
                 **kwargs):
        label = kwargs.pop('label', r'$\gamma$')
        # 从 kwargs 中取出 style，如果不存在则使用默认值
        style_to_pass = kwargs.pop('style', style) 
        super().__init__(v_start=v_start, v_end=v_end, label=label, style=style_to_pass, **kwargs) 
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.initial_phase = initial_phase
        self.final_phase = final_phase

class GluonLine(BosonLine):
    def __init__(self, v_start, v_end, amplitude=0.15, wavelength=0.2, n_cycles=16, bezier_offset=0.3, 
                 style: LineStyle = LineStyle.GLUON, # <--- 修正点：默认值在这里
                 **kwargs):
        label = kwargs.pop('label', r'$g$')
        # 从 kwargs 中取出 style，如果不存在则使用默认值
        style_to_pass = kwargs.pop('style', style)
        super().__init__(v_start=v_start, v_end=v_end, label=label, style=style_to_pass, **kwargs)
        self.amplitude = amplitude
        self.wavelength = wavelength
        self.n_cycles = n_cycles
        self.bezier_offset = bezier_offset

    def get_plot_path(self):
        # Assuming feynplot.core.gluon_methods exists and is available
        from feynplot.core.gluon_methods import generate_gluon_helix
        if self.v_start is None or self.v_end is None:
            raise ValueError("v_start 和 v_end 必须先设置")
        return generate_gluon_helix(self)

class WPlusLine(BosonLine):
    def __init__(self, v_start, v_end, 
                 zigzag_amplitude=0.2, zigzag_frequency=2.0, 
                 initial_phase=0, final_phase=0, # 添加初末相位参数
                 style: LineStyle = LineStyle.WZ,
                 **kwargs):
        label = kwargs.pop('label', r'$W^{+}$')
        
        self.zigzag_amplitude = kwargs.pop('zigzag_amplitude', zigzag_amplitude)
        self.zigzag_frequency = kwargs.pop('zigzag_frequency', zigzag_frequency)
        self.initial_phase = initial_phase
        self.final_phase = final_phase
        
        style_to_pass = kwargs.pop('style', style)
        super().__init__(v_start=v_start, v_end=v_end, label=label, style=style_to_pass, **kwargs)

class WMinusLine(BosonLine):
    def __init__(self, v_start, v_end, 
                 zigzag_amplitude=0.2, zigzag_frequency=2.0, 
                 initial_phase=0, final_phase=0, # 添加初末相位参数
                 style: LineStyle = LineStyle.WZ,
                 **kwargs):
        label = kwargs.pop('label', r'$W^{-}$')
        
        self.zigzag_amplitude = kwargs.pop('zigzag_amplitude', zigzag_amplitude)
        self.zigzag_frequency = kwargs.pop('zigzag_frequency', zigzag_frequency)
        self.initial_phase = initial_phase
        self.final_phase = final_phase
        
        style_to_pass = kwargs.pop('style', style)
        super().__init__(v_start=v_start, v_end=v_end, label=label, style=style_to_pass, **kwargs)

class ZBosonLine(BosonLine):
    def __init__(self, v_start, v_end, 
                 zigzag_amplitude=0.2, zigzag_frequency=2.0, 
                 initial_phase=0, final_phase=0, # 添加初末相位参数
                 style: LineStyle = LineStyle.WZ,
                 **kwargs):
        label = kwargs.pop('label', r'$Z^{0}$')
        
        self.zigzag_amplitude = kwargs.pop('zigzag_amplitude', zigzag_amplitude)
        self.zigzag_frequency = kwargs.pop('zigzag_frequency', zigzag_frequency)
        self.initial_phase = initial_phase
        self.final_phase = final_phase
        
        style_to_pass = kwargs.pop('style', style)
        super().__init__(v_start=v_start, v_end=v_end, label=label, style=style_to_pass, **kwargs)


class HiggsLine(BosonLine):
    def __init__(self, v_start, v_end, 
                 style: LineStyle = LineStyle.WZ, # <--- 修正点：默认值在这里
                 **kwargs):
        label = kwargs.pop('label', r'$H$')
        # 从 kwargs 中取出 style，如果不存在则使用默认值
        style_to_pass = kwargs.pop('style', style)
        super().__init__(v_start=v_start, v_end=v_end, label=label, style=style_to_pass, **kwargs)