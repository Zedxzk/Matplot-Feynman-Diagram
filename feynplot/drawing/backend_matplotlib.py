class MatplotlibBackend:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

    def render(self, vertices, lines):
        self.ax.clear()

        # 画顶点
        for v in vertices:
            self._draw_vertex(v)

        # 画线
        for line in lines:
            self._draw_line(line)

        self.ax.set_aspect('equal')
        self.ax.axis('off')
        plt.draw()
        plt.show()

    def _draw_line(self, line):
        """根据线的属性绘制线"""
        (x1, y1), (x2, y2) = line.get_coords()
        style_properties = line.get_style_properties()

        if line.style == 'photon':
            # 绘制波浪线
            self._draw_wavy_line(x1, y1, x2, y2, **style_properties)
        elif line.style == 'gluon':
            # 绘制螺旋线
            self._draw_curly_line(x1, y1, x2, y2, **style_properties)
        else:
            # 绘制普通线
            self.ax.plot([x1, x2], [y1, y2], **style_properties)

        # 添加箭头
        if line.arrow:
            self.ax.annotate(
                '', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', linewidth=1.5, color=style_properties['color'])
            )

        # 添加线标签
        if line.label:
            xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
            self.ax.text(xm, ym, line.label, fontsize=12, color=style_properties['color'])

    def _draw_wavy_line(self, x1, y1, x2, y2, **kwargs):
        """绘制波浪线"""
        import numpy as np
        num_waves = 10
        x = np.linspace(x1, x2, num_waves * 10)
        y = np.linspace(y1, y2, num_waves * 10)
        y += 0.05 * np.sin(np.linspace(0, num_waves * np.pi, num_waves * 10))
        self.ax.plot(x, y, **kwargs)

    def _draw_curly_line(self, x1, y1, x2, y2, **kwargs):
        """绘制螺旋线"""
        import numpy as np
        num_curls = 10
        x = np.linspace(x1, x2, num_curls * 10)
        y = np.linspace(y1, y2, num_curls * 10)
        y += 0.05 * np.sin(np.linspace(0, num_curls * 2 * np.pi, num_curls * 10))
        self.ax.plot(x, y, **kwargs)