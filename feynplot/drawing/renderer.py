import matplotlib.pyplot as plt
import numpy as np # Ensure numpy is imported
from feynplot.drawing.plot_functions import *
from feynplot.core.line import *


class MatplotlibBackend:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        plt.tight_layout()

    def render(self, vertices, lines):
        # 1. 清空当前轴（如果这是在同一个窗口中多次调用 render）
        self.ax.clear() 
        # 重置一些 Axes 属性，因为 clear() 会重置很多东西，包括设置的方面和轴关闭状态
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_axis_off()
        plt.tight_layout()

        # Draw lines
        for line in lines:
            self._draw_line(line)

        # Draw vertices

        # --- 绘制顶点 ---
        for v in vertices:
            if v.is_structured:
                draw_structured_vertex(self.ax, v) # 调用绘制结构化顶点的函数
            else:
                draw_point_vertex(self.ax, v)     # 调用绘制点状顶点的函数


        # Ensure the plot area fits content and maintains aspect ratio
        self.ax.autoscale_view()
        self.ax.set_aspect('equal', adjustable='box') # adjustable='box' will resize the plot box
        self.ax.axis('off') # Turn off axes

    def _draw_line(self, line):
        # Local imports for demonstration; consider moving to top if no circular dependency issues
        from feynplot.core.gluon_methods import generate_gluon_helix, generate_gluon_bezier
        from feynplot.core.photon_methods import generate_photon_wave # <--- 确保在这里有这个导入

        # <--- 确保 line_plot_options 和 label_text_options 在这里定义
        line_plot_options = line.get_plot_properties() # <--- 这一行必须在这里！
        label_text_options = line.get_label_properties() # <--- 这一行也必须在这里！


        # 在原代码中使用 draw_gluon_line 函数
        if isinstance(line, GluonLine):
            draw_gluon_line(self.ax, line, line_plot_options, label_text_options)
                
        elif isinstance(line, PhotonLine):  # <--- 添加对 PhotonLine 的处理
            print('Detected PhotonLine, drawing wave path')
            draw_photon_wave(self.ax, line, line_plot_options, label_text_options)

        elif isinstance(line, (WPlusLine, WMinusLine, ZBosonLine)):
            draw_WZ_zigzag_line(self.ax, line, line_plot_options, label_text_options) 
        
        elif isinstance(line, FermionLine): # <-- Add this block for FermionLine
            # Call the dedicated drawing function for fermion lines
            draw_fermion_line(self.ax, line, line_plot_options, label_text_options)


        else: # Handle generic lines (straight, wavy, curly)
            (x1, y1), (x2, y2) = line.get_coords()

            if line.style == LineStyle.PHOTON:
                # Pass all line_plot_options to _draw_wavy_line
                self._draw_wavy_line(x1, y1, x2, y2, **line_plot_options)
            elif line.style == LineStyle.GLUON:
                # Pass all line_plot_options to _draw_curly_line
                self._draw_curly_line(x1, y1, x2, y2, **line_plot_options)
            else:
                self.ax.plot([x1, x2], [y1, y2], **line_plot_options)

            # Draw arrow for generic lines
            if line.arrow:
                arrow_props = dict(arrowstyle='->',
                                   linewidth=line_plot_options.get('linewidth', 1.5),
                                   color=line_plot_options.get('color', 'black'))
                # You can merge specific arrow properties from line.plotConfig if needed
                # e.g., arrow_props.update(line.plotConfig.get('arrowprops', {}))

                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                if length > 0:
                    # Using ax.arrow for better control over head size relative to line length
                    # head_length and head_width are in data coordinates
                    head_length_abs = 0.08 # Absolute head length, adjust as needed
                    head_width_abs = 0.08 # Absolute head width, adjust as needed

                    # Adjust for very short lines to avoid giant arrows
                    if length < head_length_abs * 2: # If line is too short, make arrow smaller
                        head_length_abs = length / 2
                        head_width_abs = length / 2

                    # Calculate arrow tail based on desired head length
                    arrow_dx = (x2 - x1) * (1 - head_length_abs / length)
                    arrow_dy = (y2 - y1) * (1 - head_length_abs / length)

                    self.ax.arrow(x1, y1, arrow_dx, arrow_dy,
                                  head_width=head_width_abs, head_length=head_length_abs,
                                  fc=arrow_props['color'], ec=arrow_props['color'],
                                  linewidth=arrow_props['linewidth'],
                                  length_includes_head=True) # Arrow head length included in total line length
                # Alternatively, use annotate for more complex arrow styles
                # self.ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=arrow_props)

            # Draw label for generic lines
            if line.label:
                xm, ym = (x1 + x2) / 2 + line.label_offset[0], (y1 + y2) / 2 + line.label_offset[1]
                self.ax.text(xm, ym, line.label, **label_text_options)

    def _draw_wavy_line(self, x1, y1, x2, y2, **kwargs):
        """Draws a wavy line. Passes all remaining kwargs to ax.plot()."""
        num_waves = kwargs.pop('num_waves', 10) # Pop custom parameters first
        amplitude = kwargs.pop('amplitude', 0.05)

        x = np.linspace(x1, x2, num_waves * 10)
        y = np.linspace(y1, y2, num_waves * 10)
        y_offset_factor = np.sin(np.linspace(0, num_waves * np.pi, num_waves * 10))

        # Calculate perpendicular direction for wave
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        if length > 1e-9:
            nx = -dy / length
            ny = dx / length
            x_wavy = x + amplitude * nx * y_offset_factor
            y_wavy = y + amplitude * ny * y_offset_factor
        else: # Handle zero-length line case
            x_wavy, y_wavy = x, y

        self.ax.plot(x_wavy, y_wavy, **kwargs) # Pass remaining kwargs to plot

    def _draw_curly_line(self, x1, y1, x2, y2, **kwargs):
        """Draws a curly line (for generic GLUON style). Passes all remaining kwargs to ax.plot()."""
        num_curls = kwargs.pop('num_curls', 10) # Pop custom parameters first
        amplitude = kwargs.pop('amplitude', 0.05)

        x = np.linspace(x1, x2, num_curls * 10)
        y = np.linspace(y1, y2, num_curls * 10)
        y_offset_factor = np.sin(np.linspace(0, num_curls * 2 * np.pi, num_curls * 10))

        # Calculate perpendicular direction for curl
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        if length > 1e-9:
            nx = -dy / length
            ny = dx / length
            x_curly = x + amplitude * nx * y_offset_factor
            y_curly = y + amplitude * ny * y_offset_factor
        else: # Handle zero-length line case
            x_curly, y_curly = x, y

        self.ax.plot(x_curly, y_curly, **kwargs) # Pass remaining kwargs to plot

    def _draw_vertex(self, vertex):
        """Draws a vertex using ax.scatter() and passes all relevant parameters."""
        x, y = vertex.x, vertex.y
        
        # Get properties for ax.scatter()
        scatter_plot_options = vertex.get_scatter_properties()
        # Get properties for ax.text()
        label_text_options = vertex.get_scatter_properties()
        # 1. 获取顶点的绘图属性 (例如：标记样式、大小、颜色)
        vertex_plot_options = vertex.get_scatter_properties() 
        
        # 2. 绘制顶点标记
        self.ax.scatter(vertex.x, vertex.y, **vertex_plot_options)

        # 3. 获取标签的样式属性
        label_text_options = vertex.get_label_properties()   # 这个字典不应该包含 's'

        # --- 调试打印 START ---
        # print(f"DEBUG: 正在绘制顶点标签: '{vertex.label}'")
        # print(f"DEBUG: 从 Vertex.get_label_properties() 获取的标签样式选项: {label_text_options}")
        # --- 调试打印 END ---
        # Use ax.scatter() to draw the vertex, passing all relevant options
        self.ax.scatter(x, y, **scatter_plot_options)

        # Add vertex label
        if vertex.label:
            # Label position based on vertex position and label_offset
            label_x = x + vertex.label_offset[0]
            label_y = y + vertex.label_offset[1]
            
            self.ax.text(label_x, label_y,
                         vertex.label,
                         **label_text_options)

    def savefig(self, filename, **kwargs):
        """
        Saves the current figure to a file, accepting all Matplotlib savefig arguments.
        """
        self.fig.savefig(filename, **kwargs) # Pass all kwargs directly to Matplotlib's savefig


    def show(self):
        """
        显示当前 Matplotlib 图表。
        """
        plt.show() 


