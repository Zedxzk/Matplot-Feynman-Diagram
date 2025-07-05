from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import datetime # 导入 datetime 模块

class MyTimerClass(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # 设置定时器间隔为 1000 毫秒 (1秒)
        self.timer.timeout.connect(self.on_timer_timeout) # 连接 timeout 信号到槽函数
        self.start_time = None

        self.label = QLabel("等待定时器启动...")

    def start_timer(self):
        self.start_time = datetime.datetime.now() # 记录定时器启动时间
        print(f"定时器启动于: {self.start_time.strftime('%H:%M:%S.%f')}")
        self.label.setText(f"定时器启动于: {self.start_time.strftime('%H:%M:%S.%f')}")
        self.timer.start()

    def on_timer_timeout(self):
        # 当定时器触发时，获取当前时间
        current_time = datetime.datetime.now()
        print(f"定时器触发！当前时间: {current_time.strftime('%H:%M:%S.%f')}")
        
        # 计算距离定时器启动的时间间隔（可选）
        if self.start_time:
            elapsed_time = current_time - self.start_time
            print(f"距离启动已过去: {elapsed_time.total_seconds():.3f} 秒")

        self.label.setText(f"上次触发: {current_time.strftime('%H:%M:%S.%f')}\n"
                           f"已运行: {elapsed_time.total_seconds():.3f} 秒" if self.start_time else "")


if __name__ == '__main__':
    app = QApplication([])

    window = QWidget()
    layout = QVBoxLayout()
    
    timer_obj = MyTimerClass()
    layout.addWidget(timer_obj.label)
    
    window.setLayout(layout)
    window.setWindowTitle("QTimer 时间示例")
    window.show()

    # 启动定时器
    timer_obj.start_timer()

    app.exec()