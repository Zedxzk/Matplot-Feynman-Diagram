# feynplot_gui/default/default_settings.py

from typing import Dict, List, Tuple, Union

__use_relative_unit__ = True

canvas_widget_default_settings = {
    'SIGNAL_INTERVAL_MS': 100,
    'DRAG_THRESHOLD_PIXELS': 3,
    'DOUBLE_CLICK_INTERVAL_MS': 300,
    'ZOOM_FACTOR' : 1.08,
    'use_relative_unit': __use_relative_unit__,
}


canvas_controller_default_settings = {
    "NUMBER_OF_COMPARISON_POINTS": 60, 
    "SCALING_FACTOR_FOR_TOLERANCE": 1 / 30.0,
    "GRID_SIZE": 1,
    'ONLY_ALLOW_GRID_POINTS': False,
    'use_relative_unit': __use_relative_unit__,
}

navigation_widget_default_settings = {
    'use_relative_unit': __use_relative_unit__,
}

navigation_bar_controller_default_settings = {
    'SHOW_GRID': True,
    'SHOW_VERTEX_LABELS': True, 
}
