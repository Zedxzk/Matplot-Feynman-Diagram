import matplotlib.pyplot as plt

# Create a figure and axis
fig, ax = plt.subplots()

# Add text to the plot
text_obj = ax.text(0.5, 0.5, 'Hello World', fontsize=18, ha='center', va='center')

# Draw the canvas to ensure the renderer is available
fig.canvas.draw()

# Get the bounding box in pixel coordinates
renderer = fig.canvas.get_renderer()
bbox_pixel = text_obj.get_window_extent(renderer=renderer)

# Convert bounding box to data coordinates
bbox_data = bbox_pixel.transformed(ax.transData.inverted())
# Print the bounding box in data coordinates
print("Bounding box in data coordinates:")
print(f"x0: {bbox_data.x0}, y0: {bbox_data.y0}")
print(f"x1: {bbox_data.x1}, y1: {bbox_data.y1}")
plt.axhline(y=bbox_data.y0, color='green')
plt.axhline(y=bbox_data.y1, color='blue')
plt.axvline(x=bbox_data.x0, color='green')
plt.axvline(x=bbox_data.x1, color='blue')
# plt.axvline(xmin=bbox_data.x0, xmax=bbox_data.x1, color='red')
# 绘制
plt.show()

