from feynplot.core.vertex import Vertex
from feynplot.core.line import *
from feynplot.drawing.renderer import MatplotlibBackend

class FeynmanDiagram:
    def __init__(self):
        self.vertices = []
        self.lines = []
        # self.backend = MatplotlibBackend()

    def add_vertex(self, x, y, label="", **kwargs): # <--- 确保这里有 label="" 和 **kwargs
        from feynplot.core.vertex import Vertex # Local import
        # 将 label 和 kwargs 传递给 Vertex 类的构造函数
        v = Vertex(x, y, label=label, **kwargs)
        self.vertices.append(v)
        return v

    def add_line(self, v_start, v_end, line: Line = None):
        # 默认无箭头
        if line is None:
            from feynplot.core.particle import FermionLine
            line = FermionLine(arrow=False)

        line.set_vertices(v_start, v_end)
        self.lines.append(line)

    # def render(self):
    #     self.backend.render(self.vertices, self.lines)

    # def savefig(self, filename, **kwargs):
    #     """保存当前图像为文件"""
    #     self.backend.render(self.vertices, self.lines)
    #     self.backend.savefig(filename, **kwargs)
