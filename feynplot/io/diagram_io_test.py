def export_diagram_to_json(diagram_instance, filename: str):
    """
    将费曼图的当前状态导出为JSON文件。
    
    Args:
        diagram_instance: FeynmanDiagram 的实例，包含 vertices 和 lines 列表。
        filename (str): 要保存JSON文件的路径。
    Raises:
        IOError: 如果文件无法写入。
    """
    # 延迟导入 FeynmanDiagram，避免循环依赖
    from feynplot.core.diagram import FeynmanDiagram 

    if not isinstance(diagram_instance, FeynmanDiagram) or \
       not hasattr(diagram_instance, 'vertices') or not hasattr(diagram_instance, 'lines'):
        raise TypeError("Provided object is not a valid FeynmanDiagram instance (missing 'vertices' or 'lines').")

    data = {
        "vertices": [v.to_dict() for v in diagram_instance.vertices], # 调用 Vertex.to_dict()
        "lines": [l.to_dict() for l in diagram_instance.lines],       # 调用 Line.to_dict()
        "metadata": getattr(diagram_instance, 'metadata', {}) # 假设 Diagram 也有 metadata
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        raise IOError(f"Failed to write diagram to {filename}: {e}")
    print(f"Diagram exported successfully to {filename}")


def import_diagram_from_json(filename: str, diagram_instance=None):
    # from feynplot.core.diagram import FeynmanDiagram
    """
    从JSON文件导入费曼图的状态。
    如果提供了 diagram_instance，它将被清空并用导入的数据填充。
    否则，将创建一个新的 FeynmanDiagram 实例并返回。
    
    Args:
        filename (str): 要加载JSON文件的路径。
        diagram_instance (FeynmanDiagram, optional): 要填充的 FeynmanDiagram 实例。
                                                     如果为 None，将创建并返回一个新的实例。
    Returns:
        FeynmanDiagram: 包含导入数据的 FeynmanDiagram 实例。
    Raises:
        FileNotFoundError: 如果文件不存在。
        json.JSONDecodeError: 如果文件内容不是有效的JSON。
        ValueError: 如果JSON数据结构不符合预期或存在ID冲突。
        TypeError: 如果 diagram_instance 提供但不是 FeynmanDiagram 类型。
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to decode JSON from {filename}: {e}", e.doc, e.pos)
    except Exception as e:
        raise IOError(f"An unexpected error occurred while reading {filename}: {e}")

    # 延迟导入 FeynmanDiagram，避免循环依赖
    # from feynplot.core.diagram import FeynmanDiagram # 实际应用中取消注释

    if diagram_instance is None:
        diagram = FeynmanDiagram()
    elif not isinstance(diagram_instance, FeynmanDiagram):
        raise TypeError("Provided diagram_instance must be a FeynmanDiagram object.")
    else:
        diagram = diagram_instance
        diagram.clear_diagram() # 清空现有数据，如果提供了实例

    # 1. 加载顶点
    vertices_map = {} # 用于在加载线条时查找顶点对象
    for v_data in data.get("vertices", []):
        try:
            vertex = Vertex.from_dict(v_data) # 调用 Vertex.from_dict()
            print(f"Loaded vertex with ID '{vertex.id}'")
            # 应该调用 diagram.add_vertex 方法，而不是直接操作列表和集合
            # 这里是修正点
            diagram.add_vertex(vertex=vertex) # <--- 调用图的 add_vertex 方法
            vertices_map[vertex.id] = vertex
        except Exception as e:
            raise ValueError(f"Error loading vertex data for ID '{v_data.get('id', 'unknown')}': {e}") 
            print(f"Warning: Error loading vertex data for ID '{v_data.get('id', 'unknown')}': {e}")

    # 2. 加载线条
    for l_data in data.get("lines", []):
        try:
            line_type_name = l_data.get("__type__", "Line")
            line_class = _LINE_CLASS_MAPPING.get(line_type_name)
            
            if not line_class:
                print(f"Warning: Unknown line type '{line_type_name}' for line ID '{l_data.get('id', 'unknown')}'. Skipping.")
                continue

            # 调用 Line 类自身的 from_dict() 方法，这会构建一个 Line 实例
            line = line_class.from_dict(l_data, vertices_map) 
            
            # 修正点：调用 diagram.add_line 方法，并传入已构建的 Line 实例
            # 这样就可以利用 add_line 方法中的所有逻辑（ID检查、添加到内部集合等）
            print(line)
            diagram.add_line(line=line) # <--- 调用图的 add_line 方法
            
        except Exception as e:
            print(f"Warning: Error loading line data for ID '{l_data.get('id', 'unknown')}': {e}")
            raise ValueError(f"Error loading line data for ID '{l_data.get('id', 'unknown')}': {e}")

    # 假设 Diagram 类有 metadata 属性
    # diagram.metadata = data.get("metadata", {})

    print(f"Diagram imported successfully from {filename}")
    return diagram