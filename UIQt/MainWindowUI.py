from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QListWidget, QGroupBox, QVBoxLayout, \
    QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QPen, QColor, QImage
import sys

from CoordWidget import CoordWidget


class MainWindowUI(QMainWindow):
    def __init__(self):
        super(MainWindowUI, self).__init__()
        uic.loadUi("./UI/MainWindow.ui", self)

        self.points_count = 0

        # left tab (точки)
        self.points_layout: QVBoxLayout = self.findChild(QVBoxLayout, "pointsVLayout")
        self.points_layout.setAlignment(Qt.AlignTop)

        self.addStartPointBtn: QPushButton = self.findChild(QPushButton, "addStartPointBtn")
        self.addStartPointBtn.clicked.connect(self.addStartPoint)
        self.addFinishPointBtn: QPushButton = self.findChild(QPushButton, "addFinishPointBtn")
        self.addFinishPointBtn.clicked.connect(self.addFinishPoint)
        self.startMoveBtn: QPushButton = self.findChild(QPushButton, "startMoveBtn")
        self.stopMoveBtn: QPushButton = self.findChild(QPushButton, "stopMoveBtn")

        # left tab (ракурсы)
        self.angles_layout: QVBoxLayout = self.findChild(QVBoxLayout, "anglesVLayout")
        self.angles_layout.setAlignment(Qt.AlignTop)

        self.addAngleBtn: QPushButton = self.findChild(QPushButton, "addAngleBtn")
        self.deleteAngleBtn: QPushButton = self.findChild(QPushButton, "deleteAngleBtn")

        # right tab (карта)
        self.mapLabel: QLabel = self.findChild(QLabel, "mapLabel")
        # self.mapLabel.mousePressEvent = self.getPos
        self.mapLabel.mouseDoubleClickEvent = self.getPos
        self.painter: QPainter = None
        self.mapImage: QImage = None
        # self.mapLabel.setText("я карта нахуй")

        self.addMapBtn: QPushButton = self.findChild(QPushButton, "addMapBtn")
        self.addMapBtn.clicked.connect(self.addMap)
        self.deleteMapBtn: QPushButton = self.findChild(QPushButton, "deleteMapBtn")
        self.deleteMapBtn.clicked.connect(self.deleteMap)

        # right tab (3D)
        self.d3Label: QLabel = self.findChild(QLabel, "d3Label")
        # self.d3Label.setText("я 3д модель нахуй")

        self.addModelBtn: QPushButton = self.findChild(QPushButton, "addModelBtn")
        self.deleteModelBtn: QPushButton = self.findChild(QPushButton, "deleteModelBtn")

    def addStartPoint(self):
        self.points_layout.addWidget(CoordWidget(self.points_count))
        self.points_count += 1

    def addFinishPoint(self):
        self.points_layout.addWidget(CoordWidget(self.points_count))
        self.points_count += 1

    def addMap(self):
        file, _ = QFileDialog.getOpenFileName(None, 'Open File', './', "Image (*.png *.jpg *jpeg)")
        self.mapImage = QImage(file)
        self.mapLabel.setPixmap(QPixmap.fromImage(self.mapImage))

        # self.painter = QPainter(self.mapLabel.pixmap())
        # pen = QPen()
        # pen.setColor(QColor('red'))
        # pen.setWidth(55)
        # self.painter.setPen(pen)
        # self.painter.drawPoint(50, 50)
        # self.painter.end()
        print(file)

    def deleteMap(self):
        pass

    def getPos(self, event: QMouseEvent):
        if self.mapLabel.pixmap() is None:
            return
        x = event.pos().x()
        y = event.pos().y()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindowUI()
    mainWindow.show()
    sys.exit(app.exec_())
