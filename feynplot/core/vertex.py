from enum import Enum

class VertexType(Enum):
    ELECTROMAGNETIC = "electromagnetic"
    STRONG = "strong"
    WEAK = "weak"
    HIGHER_ORDER = "higher_order"

class Vertex:
    def __init__(self, x, y, vertex_type=VertexType.ELECTROMAGNETIC, label="", coupling_constant=1.0, symmetry_factor=1, color="blue", style="circle"):
        self.x = x
        self.y = y
        self.vertex_type = vertex_type
        self.label = label
        self.coupling_constant = coupling_constant
        self.symmetry_factor = symmetry_factor
        self.color = color
        self.style = style
        self.incoming = []
        self.outgoing = []
        self.particle_types = []
        self.momenta = []
        self.time_order = 0
        self.process_type = "scattering"
        self.metadata = {}

    def position(self):
        return (self.x, self.y)