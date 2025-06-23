# feynplot/io/diagram_io.py

import json
import os
import numpy as np # 如果用到numpy，也需要导入

# 【关键修正点】确保导入所有必要的FeynPlot核心类
from feynplot.core.vertex import Vertex, VertexType
from feynplot.core.line import (
    LineStyle, 
    Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine,
    WPlusLine, WMinusLine, ZBosonLine,
    # 确保导入了所有可能在_LINE_CLASS_MAPPING中使用的具体Line子类
    ElectronLine, PositronLine, MuonLine, TauLine, NeutrinoLine,
    UpQuarkLine, DownQuarkLine, CharmQuarkLine, StrangeQuarkLine,
    TopQuarkLine, BottomQuarkLine, HiggsLine, BosonLine # Add all specific line types if they exist
)

# from feynplot.core.diagram import FeynmanDiagram # 【关键修正点】顶层导入FeynmanDiagram

from typing import Dict, Any, List, TYPE_CHECKING


# # 运行时导入，但仅用于类型检查
# if TYPE_CHECKING:
from feynplot.core.diagram import FeynmanDiagram

# 定义线条类型的映射，方便在导入时根据字符串名称查找对应的类
_LINE_CLASS_MAPPING = {
    "Line": Line,
    "FermionLine": FermionLine,
    "AntiFermionLine": AntiFermionLine,
    "PhotonLine": PhotonLine,
    "GluonLine": GluonLine,
    "WPlusLine": WPlusLine,
    "WMinusLine": WMinusLine,
    "ZBosonLine": ZBosonLine,
    "ElectronLine": ElectronLine,
    "PositronLine": PositronLine,
    "MuonLine": MuonLine,
    "TauLine": TauLine,
    "NeutrinoLine": NeutrinoLine,
    "UpQuarkLine": UpQuarkLine,
    "DownQuarkLine": DownQuarkLine,
    "CharmQuarkLine": CharmQuarkLine,
    "StrangeQuarkLine": StrangeQuarkLine,
    "TopQuarkLine": TopQuarkLine,
    "BottomQuarkLine": BottomQuarkLine,
    "HiggsLine": HiggsLine,
    "BosonLine": BosonLine, # 虽然 BosonLine 通常不直接实例化，但为了完整性可以加上
    # Add any other custom Line subclasses here as you create them
}


# --- Vertex 相关的序列化和反序列化辅助函数 (保持不变) ---
def _vertex_to_dict(vertex: Vertex) -> Dict[str, Any]:
    """
    将 Vertex 实例转换为一个可序列化的字典。
    处理特殊的类型（如枚举、numpy数组）。
    这个函数由 Vertex 实例的 to_dict() 方法调用。
    """
    data = {
        'id': vertex.id,
        'x': vertex.x,
        'y': vertex.y,
        'vertex_type': vertex.vertex_type.value,
        'label': vertex.label,
        'coupling_constant': vertex.coupling_constant,
        'symmetry_factor': vertex.symmetry_factor,
        'particle_types': vertex.particle_types,
        'momenta': vertex.momenta,
        'time_order': vertex.time_order,
        'metadata': vertex.metadata,
        'hidden_vertex': vertex.hidden_vertex,
        'hidden_label': vertex.hidden_label,
        'is_selected': vertex.is_selected,
        'size': vertex.size,
        'color': vertex.color,
        'marker': vertex.marker,
        'alpha': vertex.alpha,
        'edgecolor': vertex.edgecolor,
        'linewidth': vertex.linewidth,
        'zorder': vertex.zorder,
        'label_size': vertex.label_size,
        'label_color': vertex.label_color,
        'label_offset': vertex.label_offset.tolist(),
        'is_structured': vertex.is_structured,
        'structured_radius': vertex.structured_radius,
        'structured_facecolor': vertex.structured_facecolor,
        'structured_edgecolor': vertex.structured_edgecolor,
        'structured_linewidth': vertex.structured_linewidth,
        'structured_alpha': vertex.structured_alpha,
        'zorder_structured': vertex.zorder_structured,
        'use_custom_hatch': vertex.use_custom_hatch,
        'hatch_pattern': vertex.hatch_pattern,
        'custom_hatch_line_color': vertex.custom_hatch_line_color,
        'custom_hatch_line_width': vertex.custom_hatch_line_width,
        'custom_hatch_line_angle_deg': vertex.custom_hatch_line_angle_deg,
        'custom_hatch_spacing_ratio': vertex.custom_hatch_spacing_ratio,
        # 'scatterConfig': vertex.scatterConfig
    }
    return data

def _vertex_from_dict(data: Dict[str, Any]) -> Vertex:
    """
    从字典数据创建 Vertex 实例。
    处理特殊的类型（如枚举、numpy数组）。
    这个函数由 Vertex 类的 from_dict() 类方法调用。
    """
    data_copy = data.copy()

    init_kwargs = {}

    init_kwargs['id'] = data_copy.pop('id')
    init_kwargs['x'] = data_copy.pop('x')
    init_kwargs['y'] = data_copy.pop('y')
    init_kwargs['vertex_type'] = VertexType(data_copy.pop('vertex_type'))
    init_kwargs['label_offset'] = np.array(data_copy.pop('label_offset'))
    init_kwargs['label'] = data_copy.pop('label', "")
    init_kwargs['coupling_constant'] = data_copy.pop('coupling_constant', 1.0)
    init_kwargs['symmetry_factor'] = data_copy.pop('symmetry_factor', 1)
    init_kwargs['particle_types'] = data_copy.pop('particle_types', [])
    init_kwargs['momenta'] = data_copy.pop('momenta', [])
    init_kwargs['time_order'] = data_copy.pop('time_order', 0)
    init_kwargs['metadata'] = data_copy.pop('metadata', {})
    init_kwargs['hidden_vertex'] = data_copy.pop('hidden_vertex', False)
    init_kwargs['hidden_label'] = data_copy.pop('hidden_label', False)
    init_kwargs['is_selected'] = data_copy.pop('is_selected', False)

    init_kwargs['s'] = data_copy.pop('size', 100)
    init_kwargs['c'] = data_copy.pop('color', 'blue')
    init_kwargs['marker'] = data_copy.pop('marker', 'o')
    init_kwargs['alpha'] = data_copy.pop('alpha', 1.0)
    init_kwargs['edgecolor'] = data_copy.pop('edgecolor', init_kwargs['c'])
    init_kwargs['linewidth'] = data_copy.pop('linewidth', 1.0)
    init_kwargs['zorder'] = data_copy.pop('zorder', 2)

    init_kwargs['fontsize'] = data_copy.pop('label_size', 30)
    init_kwargs['label_color'] = data_copy.pop('label_color', 'black')

    init_kwargs['is_structured'] = data_copy.pop('is_structured', False)
    init_kwargs['structured_radius'] = data_copy.pop('structured_radius', 0.5)
    init_kwargs['structured_facecolor'] = data_copy.pop('structured_facecolor', 'lightgray')
    init_kwargs['structured_edgecolor'] = data_copy.pop('structured_edgecolor', 'black')
    init_kwargs['structured_linewidth'] = data_copy.pop('structured_linewidth', 1.5)
    init_kwargs['structured_alpha'] = data_copy.pop('structured_alpha', 1.0)

    init_kwargs['use_custom_hatch'] = data_copy.pop('use_custom_hatch', False)
    init_kwargs['hatch_pattern'] = data_copy.pop('hatch_pattern', '/')
    init_kwargs['custom_hatch_line_color'] = data_copy.pop('custom_hatch_line_color', 'black')
    init_kwargs['custom_hatch_line_width'] = data_copy.pop('custom_hatch_line_width', 0.5)
    init_kwargs['custom_hatch_line_angle_deg'] = data_copy.pop('custom_hatch_line_angle_deg', 45)
    init_kwargs['custom_hatch_spacing_ratio'] = data_copy.pop('custom_hatch_spacing_ratio', 0.1)

    init_kwargs.update(data_copy.pop('scatterConfig', {}))
    init_kwargs.update(data_copy) # Add any remaining unknown kwargs

    x = init_kwargs.pop('x')
    y = init_kwargs.pop('y')

    vertex = Vertex(x, y, **init_kwargs)
    return vertex


# --- Line 相关的序列化和反序列化辅助函数 ---
def _line_to_dict(line: Line) -> Dict[str, Any]:
    """
    将 Line 实例转换为一个可序列化的字典。
    处理特殊的类型（如枚举、numpy数组），并包含类型信息。
    """
    data = {
        '__type__': line.__class__.__name__, # 存储类名以便反序列化时知道创建哪个子类
        'id': line.id,
        'v_start_id': line.v_start.id, # 存储起始顶点的ID
        'v_end_id': line.v_end.id,     # 存储结束顶点的ID
        'label': line.label,
        'label_offset': line.label_offset.tolist(), # NumPy 数组转列表
        'angleIn': line._angleIn,
        'angleOut': line._angleOut,
        'bezier_offset': line.bezier_offset,
        'linewidth': line.linewidth,
        'color': line.color,
        'linestyle': line.linestyle,
        'alpha': line.alpha,
        'zorder': line.zorder,
        'label_fontsize': line.label_fontsize,
        'label_color': line.label_color,
        'label_ha': line.label_ha,
        'label_va': line.label_va,
        'style': line.style.value, # 将 LineStyle 枚举转换为字符串值
        'is_selected': line.is_selected,
        'metadata': line.metadata # 存储未处理的 kwargs
    }

    # 处理 FermionLine 及其子类特有的属性
    if isinstance(line, FermionLine):
        data['arrow'] = line.arrow
        data['arrow_filled'] = line.arrow_filled
        data['arrow_position'] = line.arrow_position
        data['arrow_size'] = line.arrow_size
        data['arrow_line_width'] = line.arrow_line_width
        data['arrow_reversed'] = line.arrow_reversed
    
    # 处理 PhotonLine 特有的属性
    if isinstance(line, PhotonLine):
        data['amplitude'] = line.amplitude
        data['wavelength'] = line.wavelength
        data['initial_phase'] = line.initial_phase
        data['final_phase'] = line.final_phase
    
    # 处理 GluonLine 特有的属性
    if isinstance(line, GluonLine):
        data['amplitude'] = line.amplitude # 注意 GluonLine 也有 amplitude
        data['wavelength'] = line.wavelength # 注意 GluonLine 也有 wavelength
        data['n_cycles'] = line.n_cycles
        data['bezier_offset'] = line.bezier_offset # GluonLine 自身的 bezier_offset
    
    # 处理 WPlusLine, WMinusLine, ZBosonLine, HiggsLine 特有的属性 (如果它们有)
    # 假设这些类有 zigzag_amplitude 和 zigzag_frequency
    if isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
        data['zigzag_amplitude'] = line.zigzag_amplitude
        data['zigzag_frequency'] = line.zigzag_frequency

    return data

def _line_from_dict(data: Dict[str, Any], vertices_map: Dict[str, Vertex]) -> Line:
    """
    从字典数据创建 Line 实例。
    需要 vertices_map 来将顶点ID解析为实际的 Vertex 对象。
    这个函数由 Line 类的 from_dict() 类方法调用。
    """
    data_copy = data.copy()

    # 获取线条类型并查找对应的类
    line_type_name = data_copy.pop('__type__', "Line")
    line_class = _LINE_CLASS_MAPPING.get(line_type_name)

    if not line_class:
        raise ValueError(f"Unknown line type '{line_type_name}' during deserialization.")

    # 提取起始和结束顶点
    v_start_id = data_copy.pop('v_start_id')
    v_end_id = data_copy.pop('v_end_id')

    v_start = vertices_map.get(v_start_id)
    v_end = vertices_map.get(v_end_id)

    if v_start is None:
        raise ValueError(f"Start vertex with ID '{v_start_id}' not found for line '{data.get('id', 'unknown')}'.")
    if v_end is None:
        raise ValueError(f"End vertex with ID '{v_end_id}' not found for line '{data.get('id', 'unknown')}'.")

    # 构建 kwargs 字典以传递给 Line 或其子类的构造函数
    init_kwargs = {}
    init_kwargs['id'] = data_copy.pop('id')
    init_kwargs['label'] = data_copy.pop('label', '')
    init_kwargs['label_offset'] = np.array(data_copy.pop('label_offset', [0.5, 0.0]))
    init_kwargs['angleIn'] = data_copy.pop('angleIn', None)
    init_kwargs['angleOut'] = data_copy.pop('angleOut', None)
    init_kwargs['bezier_offset'] = data_copy.pop('bezier_offset', 0.3)
    init_kwargs['linewidth'] = data_copy.pop('linewidth', 1.0)
    init_kwargs['color'] = data_copy.pop('color', 'black')
    init_kwargs['linestyle'] = data_copy.pop('linestyle', '-')
    init_kwargs['alpha'] = data_copy.pop('alpha', 1.0)
    init_kwargs['zorder'] = data_copy.pop('zorder', 1)
    init_kwargs['label_fontsize'] = data_copy.pop('label_fontsize', 30)
    init_kwargs['label_color'] = data_copy.pop('label_color', 'black')
    init_kwargs['label_ha'] = data_copy.pop('label_ha', 'center')
    init_kwargs['label_va'] = data_copy.pop('label_va', 'center')
    init_kwargs['style'] = LineStyle(data_copy.pop('style')) # 从字符串还原 LineStyle 枚举
    init_kwargs['is_selected'] = data_copy.pop('is_selected', False)
    init_kwargs['metadata'] = data_copy.pop('metadata', {})

    # 处理 FermionLine 及其子类特有的属性
    if issubclass(line_class, FermionLine):
        init_kwargs['arrow'] = data_copy.pop('arrow', True)
        init_kwargs['arrow_filled'] = data_copy.pop('arrow_filled', False)
        init_kwargs['arrow_position'] = data_copy.pop('arrow_position', 0.5)
        init_kwargs['arrow_size'] = data_copy.pop('arrow_size', 10.0)
        init_kwargs['arrow_line_width'] = data_copy.pop('arrow_line_width', None)
        init_kwargs['arrow_reversed'] = data_copy.pop('arrow_reversed', False) # AntiFermionLine会设置其为True

    # 处理 PhotonLine 特有的属性
    if issubclass(line_class, PhotonLine):
        init_kwargs['amplitude'] = data_copy.pop('amplitude', 0.1)
        init_kwargs['wavelength'] = data_copy.pop('wavelength', 0.5)
        init_kwargs['initial_phase'] = data_copy.pop('initial_phase', 0)
        init_kwargs['final_phase'] = data_copy.pop('final_phase', 0)

    # 处理 GluonLine 特有的属性
    if issubclass(line_class, GluonLine):
        init_kwargs['amplitude'] = data_copy.pop('amplitude', 0.1) # GluonLine 也有 amplitude
        init_kwargs['wavelength'] = data_copy.pop('wavelength', 0.2) # GluonLine 也有 wavelength
        init_kwargs['n_cycles'] = data_copy.pop('n_cycles', 16)
        init_kwargs['bezier_offset'] = data_copy.pop('bezier_offset', 0.3) # GluonLine 自身的 bezier_offset

    # 处理 WPlusLine, WMinusLine, ZBosonLine, HiggsLine 特有的属性
    if issubclass(line_class, (WPlusLine, WMinusLine, ZBosonLine)):
        init_kwargs['zigzag_amplitude'] = data_copy.pop('zigzag_amplitude', 0.2)
        init_kwargs['zigzag_frequency'] = data_copy.pop('zigzag_frequency', 2.0)
    # 对于 HiggsLine，如果它没有特殊的构造函数参数，则不需要额外处理

    # 将所有剩余的键值对（如果存在）合并到 init_kwargs，这包括原始 kwargs 中未被明确 pop 的部分
    # 这些将最终进入 Line 类的 `self.metadata` 属性
    init_kwargs.update(data_copy) 

    # 创建 Line 实例 (使用正确的子类)
    print(f"Creating {line_class.__name__} with kwargs: {init_kwargs}")
    line = line_class(v_start=v_start, v_end=v_end,   **init_kwargs)
    print(f"Created {line_class.__name__} with ID {line.id}, Line Instance: {line}")
    return line


# --- Diagram 的导入/导出核心函数 (保持不变，因为它们通过 Line.to_dict/from_dict 间接调用上述辅助函数) ---

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
    print(f"import_diagram_from_json() is deprecated. Use feynplot.core.diagram.import_diagram_from_json() instead.")
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
        print(f"Creating new diagram instance")
        diagram = FeynmanDiagram()
    elif not isinstance(diagram_instance, FeynmanDiagram):
        raise TypeError("Provided diagram_instance must be a FeynmanDiagram object.")
    else:
        diagram = diagram_instance
        print(f"Clearing existing diagram data")
        diagram.clear_diagram() # 清空现有数据，如果提供了实例

    # 1. 加载顶点
    vertices_map = {} # 用于在加载线条时查找顶点对象
    for v_data in data.get("vertices", []):
        try:
            print(f"Loading vertex with ID '{v_data.get('id', 'unknown')}'")
            vertex = Vertex.from_dict(v_data) # 调用 Vertex.from_dict()
            print(vertex)
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
    print(f"Diagram instance: {diagram}, Vertices: {diagram.vertices}, Lines: {diagram.lines}")
    
    return diagram