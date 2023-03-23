from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QLabel, QSizePolicy


class CoordWidget(QWidget):
    def __init__(self, number: int):
        super(CoordWidget, self).__init__()
        uic.loadUi("./UI/CoordWidget.ui", self)
        self.coordBox: QGroupBox = self.findChild(QGroupBox ,"coordGroupBox")
        self.number = number
        self.coordBox.setTitle(f"Point {number}")
        self.xLine: QLineEdit = self.findChild(QLineEdit, "xLineEdit")
        self.yLine: QLineEdit = self.findChild(QLineEdit, "yLineEdit")
        self.zLine: QLineEdit = self.findChild(QLineEdit, "zLineEdit")

        self.xLabel: QLineEdit = self.findChild(QLabel, "xLabel")
        self.yLabel: QLineEdit = self.findChild(QLabel, "yLabel")
        self.zLabel: QLineEdit = self.findChild(QLabel, "zLabel")

    def setCoordinates(self, x: float, y: float, z: float):
        self.xLine.setText(str(x))
        self.yLine.setText(str(y))
        self.zLine.setText(str(z))