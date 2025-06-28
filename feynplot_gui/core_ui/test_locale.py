from PySide6.QtWidgets import QWidget, QLabel

class DummyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self.tr("Test translation"))
        self.label.setToolTip(self.tr("This is a tooltip"))
