# feynplot_gui/default/default_settings.py

from typing import Dict, List, Tuple, Union


canvas_widget_default_settings = {
    'SIGNAL_INTERVAL_MS': 100,
    'DRAG_THRESHOLD_PIXELS': 3,
    'DOUBLE_CLICK_INTERVAL_MS': 300,
    'ZOOM_FACTOR' : 1.08,
}


canvas_controller_default_settings = {
    "NUMBER_OF_COMPARISON_POINTS": 60, 
    "SCALING_FACTOR_FOR_TOLERANCE": 1 / 30.0,
    "GRID_SIZE": 1,
    'ONLY_ALLOW_GRID_POINTS': False,
}