# feynplot/core/diagram.py
from feynplot.core.vertex import Vertex
from feynplot.core.extra_text_element import TextElement
from feynplot.core.line import Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine, WPlusLine, WMinusLine, ZBosonLine
from typing import List

# from feynplot.io.diagram_io import export_diagram_to_json, import_diagram_from_json

class FeynmanDiagram:
    def __init__(self): 
        self.vertices: List[Vertex] = []  # 用于存储顶点
        self.lines: List[Line] = []  # 用于存储线条
        self.texts: List[TextElement] = []  # 用于存储额外的文本元素
        self._vertex_ids = set()  # 用于跟踪已使用的顶点ID
        self._line_ids = set()  # 用于跟踪已使用的线条ID
        self._text_ids = set()  # 用于跟踪已使用的文本ID

    def _generate_unique_vertex_id(self):
        i = 1
        while f"v_{i}" in self._vertex_ids:
            i += 1
        return f"v_{i}"

    def _generate_unique_line_id(self):
        i = 1
        while f"l_{i}" in self._line_ids:
            i += 1
        return f"l_{i}"

    def _generate_unique_text_id(self):
        i = 1
        while f"t_{i}" in self._text_ids:
            i += 1
        return f"t_{i}"

    def format_vertex_id(self, vertex_id):
        """
        将格式如 'v_11' 的ID转换为 'v_{11}'。

        Args:
            vertex_id: 原始的顶点ID字符串。

        Returns:
            格式化后的字符串。
        """
        if '_' in vertex_id:
            parts = vertex_id.split('_', 1) # 只分割一次，防止ID中出现多个下划线
            number = parts[1]
            return f"v_{{{number}}}"
        else:
            return vertex_id # 如果ID格式不符合预期，返回原ID

    def add_text(self, text_element_instance: TextElement = None, **kwargs) -> TextElement:
        """
        添加一个文本元素到图中。

        Args:
            text_element_instance (TextElement, optional): 一个已存在的 TextElement 实例。
            **kwargs: 如果没有提供实例，这些关键字参数将用于创建新的 TextElement。
            
        Returns:
            TextElement: 新添加或使用的文本元素实例。
        """
        if text_element_instance is not None:
            if not isinstance(text_element_instance, TextElement):
                raise TypeError("The 'text_element_instance' argument must be an instance of TextElement.")
            
            element = text_element_instance
        else:
            # 如果没有提供实例，就用 kwargs 创建一个
            element = TextElement(**kwargs)

        # 检查并确保 ID 唯一
        if element.id is None or element.id in self._text_ids:
            # 如果 ID 为 None 或已存在，重新生成一个
            element.id = self._generate_unique_text_id()

        self.texts.append(element)
        self._text_ids.add(element.id)
        return element

    def add_vertex(self, x: float = None, y: float = None, vertex: Vertex = None, **kwargs):
        """
        添加一个顶点到图中。
        Args:
            x (float, optional): 顶点的X坐标。当 'vertex' 参数为 None 时需要。
            y (float, optional): 顶点的Y坐标。当 'vertex' 参数为 None 时需要。
            vertex (Vertex, optional): 要添加的 Vertex 实例。如果提供此参数，则忽略 x, y 和 **kwargs。
            **kwargs: 额外的关键字参数，会传递给 Vertex 的构造函数，例如 label, id, color 等。
        
        如果 Vertex 实例没有 id 或 id 已被占用，则自动生成或抛出错误。
        如果未提供 label，则以生成的或提供的 id 作为默认 label。
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
            
            # --- 新增逻辑：如果 Vertex 实例没有 label，则使用其 id 作为 label ---
            if vertex.label is None or vertex.label == "":
                print("No label provided, using vertex_id as label, going to use:")
                print(self.format_vertex_id(vertex.id) )
                vertex.label = self.format_vertex_id(vertex.id) 



        else:
            # 如果没有提供 Vertex 实例，则根据 x, y 和 kwargs 创建
            if x is None or y is None:
                raise ValueError("Must provide 'vertex' instance OR 'x' and 'y' coordinates.")

            # 从 kwargs 中提取 'id'
            vertex_id_from_kwargs = kwargs.pop('id', None) 

            if vertex_id_from_kwargs is not None:
                if vertex_id_from_kwargs in self._vertex_ids:
                    raise ValueError(f"Vertex ID '{vertex_id_from_kwargs}' already exists. Please ensure all vertex IDs are unique.")
                vertex_id = vertex_id_from_kwargs
            else:
                vertex_id = self._generate_unique_vertex_id()
            
            # --- 新增逻辑：从 kwargs 中提取 'label'，如果不存在，则在创建 Vertex 时使用确定的 vertex_id 作为 label ---
            label_from_kwargs = kwargs.pop('label', None)
            if label_from_kwargs is None or label_from_kwargs == "": # 检查 label 是否提供或为空
                print("No label provided, using vertex_id as label, going to use:")
                print(self.format_vertex_id(vertex_id) )
                label_to_use = self.format_vertex_id(vertex_id) 
            else:
                label_to_use = label_from_kwargs # 如果提供了 label，则使用它

            # 使用 x, y, 确定的 ID, label 和所有剩余的 kwargs 创建 Vertex 实例
            vertex = Vertex(x=x, y=y, label=label_to_use, **kwargs) # <--- 修改此处，传递 label
            vertex.id = vertex_id # 将确定的 ID 赋给 Vertex 实例


        self.vertices.append(vertex)
        self._vertex_ids.add(vertex_id)
        
        # Optionally, emit a signal that the diagram has changed
        # self.emit_diagram_changed() 
        
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
            # print(f"keyword arguments for line creation: {kwargs}")
            # 使用 line_type 创建线条实例，传入顶点和所有剩余的 kwargs
            line = line_type(v_start, v_end, **kwargs)
            line.id = line_id # 将确定的 ID 赋给 Line 实例

        # 将线条添加到图中
        self.lines.append(line)
        self._line_ids.add(line_id)

        return line
    def get_text_by_id(self, text_id: str):
        """
        根据ID检索一个文本元素。
        Args:
            text_id (str): 文本的唯一标识符。
        Returns:
            TextElement: 如果找到则返回 TextElement 实例，否则返回 None。
        """
        for text in self.texts:
            if text.id == text_id:
                return text
        return None
    



    def get_vertex_by_id(self, vertex_id: str):
        """
        根据ID检索一个顶点。
        Args:
            vertex_id (str): 顶点的唯一标识符。
        Returns:
            Vertex: 如果找到则返回 Vertex 实例，否则返回 None。
        """
        for vertex in self.vertices:
            if vertex.id == vertex_id:
                return vertex
        return None

    def get_line_by_id(self, line_id: str):
        """
        根据ID检索一条线。
        Args:
            line_id (str): 线的唯一标识符。
        Returns:
            Line: 如果找到则返回 Line 实例，否则返回 None。
        """
        for line in self.lines:
            if line.id == line_id:
                return line
        return None


    def delete_text(self, text_id: str) -> bool:
        """
        根据唯一标识符删除图中的一个文本元素。
        如果找到了文本并成功删除，则返回 True；否则返回 False。
        
        Args:
            text_id (str): 要删除的文本的唯一标识符。
        Returns:
            bool: 如果成功删除则为 True，否则为 False。
        """
        original_texts_count = len(self.texts)
        self.texts = [t for t in self.texts if t.id != text_id]

        if len(self.texts) < original_texts_count:
            self._text_ids.discard(text_id)
            return True
        return False

    def remove_text(self, text_id: str) -> bool:
        """
        Same as delete_text, for backward compatibility.
        """
        return self.delete_text(text_id)

    def delete_line(self, line_id: str) -> bool:
        """
        根据唯一标识符删除图中的一条线。
        如果找到了线条并成功删除，则返回 True；否则返回 False。
        
        Args:
            line_id (str): 要删除的线的唯一标识符。
        Returns:
            bool: 如果成功删除则为 True，否则为 False。
        """
        original_lines_count = len(self.lines)
        self.lines = [line for line in self.lines if line.id != line_id]

        if len(self.lines) < original_lines_count:
            self._line_ids.discard(line_id)
            return True
        return False

    def remove_line(self, line_id: str) -> bool:
        """
        根据唯一标识符删除图中的一条线。
        如果找到了线条并成功删除，则返回 True；否则返回 False。
        
        Args:
            line_id (str): 要删除的线的唯一标识符。
        Returns:
            bool: 如果成功删除则为 True，否则为 False。
        """
        original_lines_count = len(self.lines)
        self.lines = [line for line in self.lines if line.id != line_id]

        if len(self.lines) < original_lines_count:
            self._line_ids.discard(line_id)
            return True
        return False


    def get_associated_line_ids(self, vertex_id: str) -> list[str]:
        """
        获取与指定顶点关联的所有线条的ID，但不执行删除。
        
        Args:
            vertex_id (str): 顶点的唯一标识符。
        Returns:
            list[str]: 与该顶点关联的所有线条的ID列表。如果顶点不存在，返回空列表。
        """
        # 确保顶点存在，如果不存在则没有关联线条
        if not self.get_vertex_by_id(vertex_id):
            return []

        associated_lines = []
        for line in self.lines:
            if (line.v_start and line.v_start.id == vertex_id) or \
               (line.v_end and line.v_end.id == vertex_id):
                associated_lines.append(line.id)
        return associated_lines

    def delete_vertex(self, vertex_id: str) -> bool:
        """
        根据唯一标识符删除图中的一个顶点。
        会同时删除所有与该顶点关联的线条，然后删除顶点本身。
        如果找到了顶点并成功删除，则返回 True；否则返回 False。

        Args:
            vertex_id (str): 要删除的顶点的唯一标识符。
        Returns:
            bool: 如果成功删除则为 True，否则为 False。
        """
        vertex_to_delete = self.get_vertex_by_id(vertex_id)
        if not vertex_to_delete:
            return False # 没有找到要删除的顶点

        # 1. 获取所有与该顶点关联的线条的ID
        lines_to_delete_ids = self.get_associated_line_ids(vertex_id)
        
        # 2. 先删除所有关联的线条
        for line_id_to_delete in lines_to_delete_ids:
            self.delete_line(line_id_to_delete)

        # 3. 删除顶点本身
        original_vertices_count = len(self.vertices)
        self.vertices = [v for v in self.vertices if v.id != vertex_id]

        if len(self.vertices) < original_vertices_count:
            self._vertex_ids.discard(vertex_id)
            return True
        return False
    
    def remove_vertex(self, vertex_id: str) -> bool:
        return self.delete_vertex(vertex_id)

    def delete_item(self, item_id: str, item_type: str) -> bool:
        """
        通用删除方法，根据ID和类型删除顶点或线条。
        Args:
            item_id (str): 要删除的项目的唯一标识符。
            item_type (str): 要删除的项目类型 ('vertex' 或 'line')。
        Returns:
            bool: 如果成功删除则为 True，否则为 False。
        Raises:
            ValueError: 如果 item_type 不是 'vertex' 或 'line'。
        """
        if item_type == 'vertex':
            return self.delete_vertex(item_id)
        elif item_type == 'line':
            return self.delete_line(item_id)
        else:
            raise ValueError(f"Unsupported item type for deletion: '{item_type}'. Must be 'vertex' or 'line'.")

    def update_vertex_position(self, vertex_id: str, new_x: float, new_y: float) -> bool:
        """
        更新指定顶点的坐标。
        Args:
            vertex_id (str): 要更新的顶点的唯一标识符。
            new_x (float): 新的X坐标。
            new_y (float): 新的Y坐标。
        Returns:
            bool: 如果成功更新则为 True，否则为 False。
        """
        vertex = self.get_vertex_by_id(vertex_id)
        if vertex:
            vertex.x = new_x
            vertex.y = new_y
            return True
        return False

    def get_selected_item(self, selected_id: str, selected_type: str):
        """
        根据ID和类型获取选中的对象（顶点或线条）。
        Args:
            selected_id (str): 选中的对象的ID。
            selected_type (str): 选中的对象的类型 ('vertex' 或 'line')。
        Returns:
            Vertex or Line: 如果找到则返回对应的实例，否则返回 None。
        """
        if selected_type == 'vertex':
            return self.get_vertex_by_id(selected_id)
        elif selected_type == 'line':
            return self.get_line_by_id(selected_id)
        return None

    # --- Utility Methods ---
    
    def clear_diagram(self):
        """
        清空当前费曼图中所有的顶点和线条。
        此操作会重置图表，使其为空。
        """
        self.vertices.clear()
        self.lines.clear()
        self.texts.clear()
        self._vertex_ids.clear()
        self._line_ids.clear()
        self._text_ids.clear()

    def hide_all_vertices(self):
        """隐藏图中所有顶点。"""
        for vertex in self.vertices:
            # Assumes Vertex has an 'is_visible' attribute
            vertex.hide()
    
    def show_all_vertices(self): 
        """显示图中所有顶点。"""
        for vertex in self.vertices:
            # Assumes Vertex has an 'is_visible' attribute
            vertex.show()

    def hide_all_vertice_labels(self):
        """隐藏图中所有顶点的标签。"""
        for vertex in self.vertices:
            # Assumes Vertex has a hide_label() method
            vertex.hide_label()
    
    def show_all_vertice_labels(self): 
        """显示图中所有顶点的标签。"""
        for vertex in self.vertices:
            # Assumes Vertex has a show_label() method
            vertex.show_label()


    def hide_all_line_labels(self):
        """隐藏图中所有线条的标签。"""
        for line in self.lines:
            line.hide_label()
    
    def show_all_line_labels(self): 
        """显示图中所有线条的标签。"""
        for line in self.lines:
            line.show_label()


