import numpy as np  

def find_closest_intersection_point(central_point, radius, path):
    """
    找路径中距离圆最近（即最接近圆周）的一个点。
    返回 (index, vector)：索引和交点相对中心点的向量
    """
    path = np.array(path)
    center = np.array(central_point)
    distances = np.linalg.norm(path - center, axis=1)
    diff = np.abs(distances - radius)

    idx = np.argmin(diff)
    vec = - path[idx] + center  # 向量从路径点指向中心点
    return idx, vec


def compute_path_length(path):
    """
    计算路径的总长度。
    """
    diffs = np.diff(path, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    return np.sum(segment_lengths)