# 全局 debug 开关，由 main 在启动时设置，默认为 False
DEBUG_MODE = False


def set_debug_mode(enabled: bool):
    """由 main 调用，统一设置是否输出 debug 打印。"""
    global DEBUG_MODE
    DEBUG_MODE = bool(enabled)


def cout(*args):
    """仅当 DEBUG_MODE 为 True 时打印。"""
    if DEBUG_MODE:
        print(*args)


def cout2(*args):
    """仅当 DEBUG_MODE 为 True 时打印。"""
    if DEBUG_MODE:
        print(*args)


def cout3(*args):
    """仅当 DEBUG_MODE 为 True 时打印。"""
    if DEBUG_MODE:
        print(*args)