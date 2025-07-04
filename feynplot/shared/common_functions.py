import re

# from sympy import im
from feynplot_gui.debug_utils import cout


def str2latex(label: str) -> str:
    """
    将原始标签字符串转换为 LaTeX 格式。
    如果标签看起来没有被 LaTeX 数学模式（$ 或 $$）包裹，
    则自动用 $ 包裹它。

    Args:
        label (str): 原始的标签字符串。

    Returns:
        str: 转换为 LaTeX 格式的标签字符串。
    """
    cout("Calling str2latex()")
    cout("label:", label)
    if not isinstance(label, str):
        # 如果不是字符串，直接返回其字符串表示，或者抛出错误，取决于你的需求
        # 这里为了兼容性，直接返回字符串形式
        label = str(label)

    stripped_label = label.strip()

    # 使用正则表达式更健壮地检查是否已经包含在数学模式中
    # 检查行内数学模式：以 $ 开头和结尾，中间有内容，且 $ 内部不能有未转义的 $
    is_inline_latex = re.fullmatch(r'\$.*?(?<!\\)\$', stripped_label)

    # 检查显示数学模式：以 $$ 开头和结尾，中间有内容，且 $$ 内部不能有未转义的 $ 或 $$
    is_display_latex = re.fullmatch(r'\$\$.*?(?<!\\)\$\$', stripped_label)

    # 如果标签不是行内或显示数学模式，则自动用 $ 包裹
    if not is_inline_latex and not is_display_latex:
        res = f"${label}$"
        cout(res)
        return res
    else:
        # 如果已经符合 LaTeX 数学模式，则原样返回
        return label