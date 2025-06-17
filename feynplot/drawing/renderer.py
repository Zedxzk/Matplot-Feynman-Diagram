import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, RegularPolygon  # 支持不同样式的顶点

class MatplotlibBackend:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

    def render(self, vertices, lines):
        self.ax.clear()

        # 画线
        for line in lines:
            self._draw_line(line)

        # 画顶点
        for v in vertices:
            self._draw_vertex(v)

        self.ax.set_aspect('equal')
        self.ax.axis('off')
        plt.draw()
        plt.show()

    def _draw_line(self, line):
        from feynplot.core.line import GluonLine
        from feynplot.core.gluon_methods import generate_gluon_bezier

        if isinstance(line, GluonLine):
            print('GluonLine detected')
            # 螺旋线（D轨迹）
            helix_path = line.get_plot_path()  # Nx2 numpy array
            x_helix, y_helix = helix_path[:, 0], helix_path[:, 1]

            # 贝塞尔路径（C轨迹）
            bezier_path = generate_gluon_bezier(line)  # Nx2 numpy array
            x_bezier, y_bezier = bezier_path[:, 0], bezier_path[:, 1]

            style_props = line.get_style_properties()  # 颜色、线宽等
            color = style_props.get('color', 'blue')
            linewidth = style_props.get('linewidth', 1.5)

            # 先画贝塞尔路径，用虚线表现
            self.ax.plot(x_bezier, y_bezier, linestyle='--', color=color, linewidth=linewidth * 0.8, label='Bezier Path')

            # 再画螺旋线
            self.ax.plot(x_helix, y_helix, color=color, linewidth=linewidth, label='Gluon Helix')

            # 画箭头（螺旋线末端方向）
            if line.arrow and len(x_helix) > 1:
                self.ax.annotate(
                    '',
                    xy=(x_helix[-1], y_helix[-1]),
                    xytext=(x_helix[-2], y_helix[-2]),
                    arrowprops=dict(arrowstyle='->', linewidth=1.5, color=color)
                )

            # 标签放螺旋线中点附近
            if line.label:
                mid_idx = len(x_helix) // 2
                self.ax.text(x_helix[mid_idx], y_helix[mid_idx], line.label, fontsize=12, color=color)

        else:
            # 不是 GluonLine，按原方法画普通线或其他样式
            (x1, y1), (x2, y2) = line.get_coords()
            style_properties = line.get_style_properties()

            if line.style == 'photon':
                self._draw_wavy_line(x1, y1, x2, y2, **style_properties)
            elif line.style == 'gluon':
                self._draw_curly_line(x1, y1, x2, y2, **style_properties)
            else:
                self.ax.plot([x1, x2], [y1, y2], **style_properties)

            if line.arrow:
                self.ax.annotate(
                    '', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', linewidth=1.5, color=style_properties.get('color', 'k'))
                )

            if line.label:
                xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
                self.ax.text(xm, ym, line.label, fontsize=12, color=style_properties.get('color', 'k'))



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

    def _draw_vertex(self, vertex):
        """根据顶点的属性绘制顶点"""
        x, y = vertex.x, vertex.y
        color = vertex.color
        style = vertex.style
        label = vertex.label

        # 根据样式绘制顶点
        if style == "circle":
            patch = Circle((x, y), radius=0.1, color=color, zorder=2)
        elif style == "square":
            patch = Rectangle((x - 0.1, y - 0.1), width=0.2, height=0.2, color=color, zorder=2)
        elif style == "triangle":
            patch = RegularPolygon((x, y), numVertices=3, radius=0.1, color=color, zorder=2)
        else:  # 默认样式为圆形
            patch = Circle((x, y), radius=0.1, color=color, zorder=2)

        self.ax.add_patch(patch)

        # 添加顶点标签
        if label:
            self.ax.text(x + 0.15, y + 0.15, label, fontsize=12, color=color)

    # def _draw_line(self, line):
    #     """根据线的属性绘制线"""
    #     (x1, y1), (x2, y2) = line.get_coords()
    #     if line.arrow:
    #         self.ax.annotate(
    #             '', xy=(x2, y2), xytext=(x1, y1),
    #             arrowprops=dict(arrowstyle='->', linewidth=1.5, color='k')
    #         )
    #     else:
    #         self.ax.plot([x1, x2], [y1, y2], 'k-')

    #     # 添加线标签
    #     if line.label:
    #         xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
    #         self.ax.text(xm, ym, line.label, fontsize=12, color='k')

    def savefig(self, filename, **kwargs):
        # self.fig.savefig(filename, **kwargs)
        pass