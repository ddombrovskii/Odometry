from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма
from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QLabel, QSizePolicy


class PointWidget(QWidget):
    def __init__(self, number: int):
        super(PointWidget, self).__init__()
        uic.loadUi("./UI/PointWidget.ui", self)
        self.coordBox: QGroupBox = self.findChild(QGroupBox ,"coordinatesBox")
        self.number = number
        self.coordBox.setTitle(f"Point {number}")
        self.xLine: QLineEdit = self.findChild(QLineEdit, "xLineEdit")
        self.yLine: QLineEdit = self.findChild(QLineEdit, "yLineEdit")
        self.zLine: QLineEdit = self.findChild(QLineEdit, "zLineEdit")

        self.xLabel: QLineEdit = self.findChild(QLabel, "xLabel")
        self.yLabel: QLineEdit = self.findChild(QLabel, "yLabel")
        self.zLabel: QLineEdit = self.findChild(QLabel, "zLabel")

    def setCoordinates(self, x, y, z=0.):
        self.xLine.setText(str(float(x)))
        self.yLine.setText(str(float(y)))
        self.zLine.setText(str(float(z)))