import numpy as np
import matplotlib.pyplot as plt

def generate_base_path(npoints=1000):
    """Generate a parabolic base path with uniform arc length sampling"""
    # Dense sampling for arc length calculation
    x_dense = np.linspace(-2, 2, 10000)
    y_dense = -x_dense**2 + 4
    curve_dense = np.column_stack([x_dense, y_dense])

    # Compute arc length
    deltas = np.diff(curve_dense, axis=0)
    segment_lengths = np.sqrt((deltas**2).sum(axis=1))
    arc_lengths = np.concatenate([[0], np.cumsum(segment_lengths)])
    total_length = arc_lengths[-1]

    # Uniform arc length sampling
    target_lengths = np.linspace(0, total_length, npoints)
    x_uniform = np.interp(target_lengths, arc_lengths, x_dense)
    y_uniform = -x_uniform**2 + 4
    base_path = np.column_stack([x_uniform, y_uniform])
    return base_path

def simulate_combined_motion(base_path, radius=0.5, n_rotations=8):
    """Simulate a point rotating around a center that moves along base_path"""
    npoints = len(base_path)
    angles = np.linspace(0, 2 * np.pi * n_rotations, npoints)
    dx = radius * np.cos(angles)
    dy = radius * np.sin(angles)
    combined_path = base_path + np.column_stack([dx, dy])
    return combined_path

# Generate base path with uniform arc length sampling
base_path = generate_base_path(npoints=1000)

# Simulate combined motion
combined_path = simulate_combined_motion(base_path, radius=0.5, n_rotations=8)

# Plot the result
plt.figure(figsize=(10, 6))
plt.plot(base_path[:, 0], base_path[:, 1], 'k--', label='Base Path (Center)')
plt.plot(combined_path[:, 0], combined_path[:, 1], 'b-', label='Combined Motion Path')
plt.axis('equal')
plt.legend()
plt.title('Combined Motion with Uniform Spiral Peaks')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()

