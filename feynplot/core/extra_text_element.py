from PySide6.QtGui import QColor

class TextElement:
    _next_id = 1
    
    # 定义一个黑名单，用于在序列化时排除内部或非用户可编辑的属性
    __exclude__ = ['id', 'is_selected']

    def __init__(self, text: str, x: float = 0.0, y: float = 0.0, size : int = 12, color = 'black', bold: bool = False, italic: bool = False, ha: str = 'center', va: str = 'center'):
        self.id = TextElement._next_id
        TextElement._next_id += 1
        
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.bold = bold
        self.italic = italic
        self.ha = ha
        self.va = va
        self.clip_on = True
        self.is_selected = False # 用于UI同步选择状态

    def __repr__(self):
        return f"TextElement(id={self.id}, text='{self.text}', x={self.x}, y={self.y})"

    def update_from_dict(self, data: dict):
        """
        根据传入的字典更新对象的属性。
        """
        for key, value in data.items():
            # 仅更新存在的属性
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> dict:
        """
        返回一个包含所有可编辑属性的字典，自动排除黑名单中的属性。
        """
        return {
            key: value for key, value in self.__dict__.items()
            if key not in self.__exclude__
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        根据传入的字典创建一个新的 TextElement 对象。
        """
        # 使用字典解包 **data，让 __init__ 自动匹配参数
        return cls(**data)
    

    def to_matplotlib_kwargs(self) -> dict:
        """
        返回一个适合作为 ax.text() 关键字参数的字典。
        """
        # 从 to_dict() 获取所有基本属性
        props = self.to_dict()

        # 调整参数名以匹配 Matplotlib
        kwargs = {
            'x': props.pop('x'),
            'y': props.pop('y'),
            's': r'{}'.format(props.pop('text')),  # 转换为原始字符串
            'size': props.pop('size'),
            'color': props.pop('color'),
            'horizontalalignment': props.pop('ha'),
            'verticalalignment': props.pop('va'),
            'clip_on': props.pop('clip_on'),
        }

        # 根据 bold 和 italic 布尔值设置 Matplotlib 的字体样式
        if props.pop('bold'):
            kwargs['fontweight'] = 'bold'
        if props.pop('italic'):
            kwargs['fontstyle'] = 'italic'

        return kwargs