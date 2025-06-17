from feynplot.core.vertex import Vertex
from feynplot.core.line import Line
from feynplot.drawing.renderer import MatplotlibBackend

class FeynmanDiagram:
    def __init__(self):
        self.vertices = []
        self.lines = []
        self.backend = MatplotlibBackend()

    def add_vertex(self, x, y):
        vertex = Vertex(x, y)
        self.vertices.append(vertex)
        return vertex

    def add_line(self, v_start, v_end, line: Line = None):
        # 默认无箭头
        if line is None:
            from feynplot.core.particle import FermionLine
            line = FermionLine(arrow=False)

        line.set_vertices(v_start, v_end)
        self.lines.append(line)

    def render(self):
        self.backend.render(self.vertices, self.lines)

    def savefig(self, filename, **kwargs):
        """保存当前图像为文件"""
        self.backend.render(self.vertices, self.lines)
        self.backend.savefig(filename, **kwargs)
