class Line:
    def __init__(self, style='fermion', label='', arrow=False, **kwargs):
        """
        初始化线对象。

        :param style: 线的类型，支持 'fermion'（费米子，实线）、'photon'（光子，波浪线）、
                     'gluon'（胶子，螺旋线）、'wz'（W/Z 玻色子，折线）等。
        :param label: 线的标签。
        :param arrow: 是否绘制箭头。
        :param kwargs: 额外绘图参数（颜色、虚线等）。
        """
        self.style = style
        self.label = label
        self.arrow = arrow
        self.v_start = None
        self.v_end = None
        self.options = kwargs  # 额外绘图参数（颜色、虚线等）

    def set_vertices(self, v_start, v_end):
        """
        设置线的起点和终点顶点。

        :param v_start: 起点顶点。
        :param v_end: 终点顶点。
        """
        self.v_start = v_start
        self.v_end = v_end

    def get_coords(self):
        """
        获取线的起点和终点坐标。

        :return: 起点和终点的坐标，格式为 ((x1, y1), (x2, y2))。
        """
        return (self.v_start.x, self.v_start.y), (self.v_end.x, self.v_end.y)

    def get_style_properties(self):
        """
        根据线的类型返回绘图属性。

        :return: 包含线型、颜色等属性的字典。
        """
        style_properties = {
            'fermion': {'linestyle': '-', 'color': 'black'},  # 费米子：实线
            'photon': {'linestyle': '--', 'color': 'blue'},    # 光子：波浪线
            'gluon': {'linestyle': '-', 'color': 'red'},      # 胶子：螺旋线
            'wz': {'linestyle': '-.', 'color': 'green'},      # W/Z 玻色子：折线
        }
        return style_properties.get(self.style, {'linestyle': '-', 'color': 'black'})  # 默认：实线