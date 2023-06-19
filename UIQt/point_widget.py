from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма
from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QLabel, QSizePolicy, QStyle, QPushButton


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

        deleteIconPixmap = self.style().standardIcon(getattr(QStyle, "SP_DockWidgetCloseButton"))
        self.deleteBtn: QPushButton = self.findChild(QPushButton, "deleteBtn")
        self.deleteBtn.setIcon(deleteIconPixmap)
        self.deleteBtn.clicked.connect(self.delete_clicked)

    def setCoordinates(self, x, y, z=0.):
        self.xLine.setText(str(float(x)))
        self.yLine.setText(str(float(y)))
        self.zLine.setText(str(float(z)))

    def delete_clicked(self):
        self.deleteLater()

    def set_number(self, number: int):
        self.number = number
        self.coordBox.setTitle(f"Point {number}")