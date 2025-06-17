import matplotlib.pyplot as plt
from feynplot.core.line import GluonLine
from feynplot.core.gluon_methods import generate_gluon_bezier

def main():
    # 创建 GluonLine 实例并设置参数
    gluon = GluonLine(
        amplitude=0.1,
        wavelength=0.2,
        n_cycles=10,
        bezier_offset=0.3,
    )
    gluon.v_start = (0, 0)
    gluon.v_end = (2, 0)
    gluon.angleOut = 0.0
    gluon.angleIn = 150.0

    # 获取螺旋线轨迹点（D轨迹）
    helix_path = gluon.get_plot_path()  # Nx2 numpy array

    # 获取贝塞尔路径点（C轨迹）
    bezier_path = generate_gluon_bezier(gluon)  # Nx2 numpy array

    # 绘图
    plt.figure(figsize=(10, 5))
    
    # 画贝塞尔路径（C点轨迹）
    plt.plot(bezier_path[:, 0], bezier_path[:, 1], label="Bezier Path (C points)", color='green', linewidth=2)

    # 画螺旋线轨迹（D点轨迹）
    plt.plot(helix_path[:, 0], helix_path[:, 1], label="Gluon Helix (D points)", color='blue', linewidth=1)

    # 起点终点
    plt.scatter([gluon.v_start[0], gluon.v_end[0]], [gluon.v_start[1], gluon.v_end[1]], 
                color='red', label='Endpoints', zorder=5)

    plt.axis('equal')
    plt.title("GluonLine: Bezier Path & Helix Path")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
