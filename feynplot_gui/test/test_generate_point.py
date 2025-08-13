import matplotlib.pyplot as plt

fig, ax = plt.subplots()

# Figure 尺寸 (英寸)
width_inch, height_inch = fig.get_size_inches()
# DPI
dpi = fig.dpi

# 实际像素
width_px  = int(width_inch * dpi)
height_px = int(height_inch * dpi)

print(f"Canvas 像素大小: {width_px} x {height_px}")
