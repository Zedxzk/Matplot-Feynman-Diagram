# feynplot/core/diagram.py

# 确保导入了必要的类和模块
# 例如:
from feynplot.core.vertex import Vertex
from feynplot.core.line import Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine, WPlusLine, WMinusLine, ZBosonLine
# from feynplot.core.particle import FermionLine # 如果 FermionLine 在这里定义

class FeynmanDiagram:
    def __init__(self):
        self.vertices = []
        self.lines = []
        self._vertex_ids = set() # 用于跟踪已使用的顶点ID
        self._line_ids = set()   # 用于跟踪已使用的线条ID
        # ... 其他初始化，比如计数器用于生成ID

    # 假设这里有 _generate_unique_vertex_id 和 _generate_unique_line_id 方法
    def _generate_unique_vertex_id(self):
        # 这是一个示例实现，请根据你的实际需求调整
        i = 1
        while f"v_{i}" in self._vertex_ids:
            i += 1
        return f"v_{i}"

    def _generate_unique_line_id(self):
        # 这是一个示例实现，请根据你的实际需求调整
        i = 1
        while f"l_{i}" in self._line_ids:
            i += 1
        return f"l_{i}"

    def add_vertex(self, x: float = None, y: float = None, vertex: Vertex = None, **kwargs): # <<< 修改签名，添加 x 和 y
        """
        添加一个顶点到图中。
        Args:
            x (float, optional): 顶点的X坐标。当 'vertex' 参数为 None 时需要。
            y (float, optional): 顶点的Y坐标。当 'vertex' 参数为 None 时需要。
            vertex (Vertex, optional): 要添加的 Vertex 实例。如果提供此参数，则忽略 x, y 和 **kwargs。
            **kwargs: 额外的关键字参数，会传递给 Vertex 的构造函数，例如 label, id, color 等。
        
        如果 Vertex 实例没有 id 或 id 已被占用，则自动生成或抛出错误。
        """
        if vertex is not None:
            # 如果提供了 Vertex 实例，直接使用它
            if not isinstance(vertex, Vertex):
                raise TypeError("The 'vertex' argument must be an instance of Vertex.")
            
            # 检查 ID 唯一性并赋值
            if vertex.id is not None:
                if vertex.id in self._vertex_ids:
                    raise ValueError(f"Vertex ID '{vertex.id}' already exists. Please ensure all vertex IDs are unique.")
                vertex_id = vertex.id
            else:
                vertex_id = self._generate_unique_vertex_id()
                vertex.id = vertex_id # 将生成的 ID 赋给 Vertex 实例

        else:
            # 如果没有提供 Vertex 实例，则根据 x, y 和 kwargs 创建
            if x is None or y is None:
                raise ValueError("Must provide 'vertex' instance OR 'x' and 'y' coordinates.")

            # 从 kwargs 中提取 'id'，如果存在的话
            vertex_id_from_kwargs = kwargs.pop('id', None) 

            if vertex_id_from_kwargs is not None:
                if vertex_id_from_kwargs in self._vertex_ids:
                    raise ValueError(f"Vertex ID '{vertex_id_from_kwargs}' already exists. Please ensure all vertex IDs are unique.")
                vertex_id = vertex_id_from_kwargs
            else:
                vertex_id = self._generate_unique_vertex_id()
            
            # 使用 x, y 和所有剩余的 kwargs 创建 Vertex 实例
            vertex = Vertex(x=x, y=y, **kwargs) # <<< 将 x, y 作为明确参数传入
            vertex.id = vertex_id # 将确定的 ID 赋给 Vertex 实例

        self.vertices.append(vertex)
        self._vertex_ids.add(vertex_id)
        return vertex

    def add_line(self, v_start: Vertex = None, v_end: Vertex = None, 
                 line: Line = None, line_type: type = FermionLine, **kwargs):
        """
        添加一条线到图中。
        
        Args:
            v_start (Vertex, optional): 线的起始顶点。当 'line' 参数为 None 时需要。
            v_end (Vertex, optional): 线的结束顶点。当 'line' 参数为 None 时需要。
            line (Line, optional): 要添加的 Line 实例。如果提供此参数，则忽略 v_start, v_end, line_type 和 **kwargs。
            line_type (type, optional): 当 'line' 参数为 None 时，要创建的 Line 类型（例如 FermionLine, PhotonLine 等）。
                                        默认为 FermionLine。
            **kwargs: 额外的关键字参数，会传递给 line_type 的构造函数，例如 label, id, arrow 等。

        如果 Line 实例没有 id 或 id 已被占用，则自动生成或抛出错误。
        """
        if line is not None:
            # 如果提供了 Line 实例，直接使用它
            if not isinstance(line, Line):
                raise TypeError("The 'line' argument must be an instance of Line or its subclass.")
            
            # 检查 ID 唯一性并赋值
            if line.id is not None:
                if line.id in self._line_ids:
                    raise ValueError(f"Line ID '{line.id}' already exists. Please ensure all line IDs are unique.")
                line_id = line.id
            else:
                line_id = self._generate_unique_line_id()
                line.id = line_id
            
            # 检查 Line 实例是否已经有顶点，如果没有，则抛出错误或根据需要设置
            if line.v_start is None or line.v_end is None:
                if v_start is None or v_end is None:
                    raise ValueError("Provided Line instance has no vertices, and v_start/v_end were not specified.")
                line.set_vertices(v_start, v_end) # 设置线的顶点

        else:
            # 如果没有提供 Line 实例，则根据 v_start, v_end 和 line_type 创建
            if v_start is None or v_end is None:
                raise ValueError("Must provide 'line' instance OR 'v_start' and 'v_end' vertices.")
            if not issubclass(line_type, Line):
                raise TypeError("The 'line_type' must be a subclass of Line.")

            # 从 kwargs 中提取 'id'，如果存在的话，用于唯一性检查
            line_id_from_kwargs = kwargs.pop('id', None)

            if line_id_from_kwargs is not None:
                if line_id_from_kwargs in self._line_ids:
                    raise ValueError(f"Line ID '{line_id_from_kwargs}' already exists. Please ensure all line IDs are unique.")
                line_id = line_id_from_kwargs
            else:
                line_id = self._generate_unique_line_id()
            
            # 使用 line_type 创建线条实例，传入顶点和所有剩余的 kwargs
            line = line_type(v_start, v_end, **kwargs)
            line.id = line_id # 将确定的 ID 赋给 Line 实例

        # 将线条添加到图中
        self.lines.append(line)
        self._line_ids.add(line_id)
        return line
    
    # Add this method to your FeynmanDiagram class
    def get_vertex_by_id(self, vertex_id):
        """Retrieves a vertex by its ID."""
        for vertex in self.vertices:
            if vertex.id == vertex_id:
                return vertex
        return None # Return None if not found

    # Add this method to your FeynmanDiagram class
    def get_line_by_id(self, line_id):
        """Retrieves a line by its ID."""
        for line in self.lines:
            if line.id == line_id:
                return line
        return None # Return None if not found