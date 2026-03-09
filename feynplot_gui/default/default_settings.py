# feynplot_gui/default/default_settings.py

from typing import Dict, List, Any

# ----------------------------------------------------
# 1. 核心通用设置
# ----------------------------------------------------
# 所有模块共享的全局配置
GENERAL_SETTINGS: Dict[str, Any] = {
    'USE_RELATIVE_UNIT': True,
    'TRANSPARENT_BACKGROUND': False,
    'ZOOM_FACTOR': 1.08,
}

# ----------------------------------------------------
# 2. 模块特定的默认设置
# ----------------------------------------------------
# 这些设置可以继承 GENERAL_SETTINGS，或者包含特有配置
CANVAS_WIDGET_DEFAULTS: Dict[str, Any] = {
    'FPS_LIMIT': 10,                 # 默认 FPS
    'FPS_MIN': 2,                    # 最小 FPS
    'FPS_MAX': 25,                   # 最大 FPS
    'SIGNAL_INTERVAL_MS': 1000 // 10, # 根据默认 FPS 计算 (100ms)
    'DRAG_THRESHOLD_PIXELS': 3,
    'DOUBLE_CLICK_INTERVAL_MS': 300,
    **GENERAL_SETTINGS,  # 合并通用设置
}

CANVAS_CONTROLLER_DEFAULTS: Dict[str, Any] = {
    "NUMBER_OF_COMPARISON_POINTS": 60, 
    "SCALING_FACTOR_FOR_TOLERANCE": 1 / 30.0,
    "GRID_SIZE": 1,
    'ONLY_ALLOW_GRID_POINTS': False,
    # 方向键步长（数据坐标）：默认 0.1，Ctrl 精细 0.01，Shift 大步 0.25（平移与移动顶点共用）
    "ARROW_STEP": 0.1,
    "ARROW_STEP_FINE": 0.01,
    "ARROW_STEP_LARGE": 0.25,
    # 格点模式下方向键步长：默认 1，Shift 2，Ctrl 保持 1
    "ARROW_STEP_GRID": 1,
    "ARROW_STEP_GRID_LARGE": 2,
    **GENERAL_SETTINGS,
}

NAVIGATION_WIDGET_DEFAULTS: Dict[str, Any] = {
    **GENERAL_SETTINGS,
}

NAVIGATION_BAR_CONTROLLER_DEFAULTS: Dict[str, Any] = {
    'SHOW_GRID': True,
    'SHOW_VERTEX_LABELS': True, 
}


# ----------------------------------------------------
# 3. 多语言文本数据
# ----------------------------------------------------
# 将提示信息从配置中分离出来，便于国际化
TIPS: Dict[str, List[str]] = {
    'zh_CN': [
        "使用鼠标滚轮缩放画布。",
        "按住画布可以拖动视图。",
        "保存为图片时，只有zorder>0的元素会被保存。",
        "双击画布空白处可以添加新顶点。",
        "双击画布上的顶点和线条可以修改其属性。",
        "选中一个线条或顶点，右键单击可以修改其属性。",
        "网格会被保存在图像中，如果需要隐藏网格，在右侧栏中关闭网格显示。",
    ],
    'en': [
        "Use the mouse wheel to zoom the canvas.",
        "Hold the canvas to drag the view.",
        "When saving as an image, only elements with zorder > 0 will be saved.",
        "Double-clicking on an empty area of the canvas adds a new vertex.",
        "Double-clicking on a vertex or line on the canvas allows you to modify its properties.",
        "Right-clicking on a selected line or vertex allows you to modify its properties.",
        "The grid will be saved in the image. To hide the grid, turn off grid display in the right sidebar.",
    ]
}