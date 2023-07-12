from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма
from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QLabel, QSizePolicy, QStyle, QPushButton


# UNUSED
class PointWidget(QWidget):
    def __init__(self, number: int):
        super(PointWidget, self).__init__()
        uic.loadUi("./UI/PointWidget.ui", self)
        self.coordBox: QGroupBox = self.findChild(QGroupBox, "coordinatesBox")
        self.number = number
        self.coordBox.setTitle(f"Point {number}")
        self.xLine: QLineEdit = self.findChild(QLineEdit, "xLineEdit")
        self.yLine: QLineEdit = self.findChild(QLineEdit, "yLineEdit")
        self.zLine: QLineEdit = self.findChild(QLineEdit, "zLineEdit")

        self.xLabel: QLineEdit = self.findChild(QLabel, "xLabel")
        self.yLabel: QLineEdit = self.findChild(QLabel, "yLabel")
        self.zLabel: QLineEdit = self.findChild(QLabel, "zLabel")

        delete_icon_pixmap = self.style().standardIcon(getattr(QStyle, "SP_DockWidgetCloseButton"))
        self.deleteBtn: QPushButton = self.findChild(QPushButton, "deleteBtn")
        self.deleteBtn.setIcon(delete_icon_pixmap)
        self.deleteBtn.clicked.connect(self.delete_clicked)
        self.delete_callback = None

    def set_coordinates(self, x, y, z):
        self.xLine.setText(f"{float(x):.3f}")
        self.yLine.setText(f"{float(y):.3f}")
        self.zLine.setText(f"{float(z):.3f}")

    def delete_clicked(self):
        if self.delete_callback is not None:
            self.delete_callback()
        self.deleteLater()

    def set_number(self, number: int):
        self.number = number
        self.coordBox.setTitle(f"Point {number}")