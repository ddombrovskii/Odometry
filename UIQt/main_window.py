from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QListWidget, QGroupBox, QVBoxLayout, \
    QFileDialog, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QPen, QColor, QImage, QPaintEngine
import sys
from PyQt5.QtGui import QCloseEvent

from UIQt.scene_viewer_widget import SceneViewerWidget
from point_widget import PointWidget


class MainWindowUI(QMainWindow):
    def __init__(self):
        super(MainWindowUI, self).__init__()
        uic.loadUi("./UI/MainWindow.ui", self)

        self.points_count = 0
        self.start_point = None
        self.finish_point = None

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
        self.mapLabel.mousePressEvent = self.singleMapClick
        self.mapLabel.mouseDoubleClickEvent = self.doubleMapClick
        self.mapPixmap: QPixmap = None

        self.addMapBtn: QPushButton = self.findChild(QPushButton, "addMapBtn")
        self.addMapBtn.clicked.connect(self.addMap)
        self.deleteMapBtn: QPushButton = self.findChild(QPushButton, "deleteMapBtn")
        self.deleteMapBtn.clicked.connect(self.deleteMap)

        # right tab (3D)
        self.d3Layout = self.findChild(QVBoxLayout, "d3TabVLayout")
        self.glWidget: SceneViewerWidget = SceneViewerWidget(self)
        self.d3Layout.insertWidget(0, self.glWidget)

        self.addModelBtn: QPushButton = self.findChild(QPushButton, "addModelBtn")
        self.deleteModelBtn: QPushButton = self.findChild(QPushButton, "deleteModelBtn")

        timer_update = QTimer(self)
        timer_update.setInterval(20)  # period, in milliseconds
        timer_update.timeout.connect(self.glWidget.updateGL)
        timer_update.start()
        timer_paint = QTimer(self)
        timer_paint.setInterval(33)  # period, in milliseconds
        timer_paint.timeout.connect(self.glWidget.paintGL)
        timer_paint.start()
        self.closeEvent(QCloseEvent())

    def closeEvent(self, a0) -> None:
        self.glWidget.clean_up()

    def singleMapClick(self, event: QMouseEvent):
        if self.mapPixmap is None:
            return
        x, y = self.get_correct_coordinates(event.pos())
        newPoint = PointWidget(self.points_count)
        newPoint.setCoordinates(x, y)
        self.points_layout.addWidget(newPoint)
        self.points_count += 1
        if event.button() == Qt.LeftButton:
            self.start_point = newPoint
            self.draw_something(x, y, width=15, color='blue')
        if event.button() == Qt.RightButton:
            self.finish_point = newPoint
            self.draw_something(x, y, width=15, color='green')

    def addStartPoint(self):
        print("add button clicked")

    def addFinishPoint(self):
        print("add button clicked")

    def addMap(self):
        file, _ = QFileDialog.getOpenFileName(None, 'Open File', './', "Image (*.png *.jpg *jpeg)")
        if file != '':
            self.deleteMap()
            self.mapPixmap = QPixmap(file)
            self.update_map_image()
            print(file)

    def deleteMap(self):
        self.mapLabel.setPixmap(QPixmap())
        self.mapPixmap = None
        self.start_point = None
        self.finish_point = None
        for i in reversed(range(self.points_layout.count())):
            self.points_layout.itemAt(i).widget().deleteLater()

    def get_correct_coordinates(self, pos):
        x = pos.x() * self.mapPixmap.size().width() // self.mapLabel.width()
        y = pos.y() * self.mapPixmap.size().height() // self.mapLabel.height()
        return x, y

    def doubleMapClick(self, event: QMouseEvent):
        pass

    def draw_something(self, x, y, width=15, color='red'):
        painter = QPainter(self.mapPixmap)
        pen = QPen()
        pen.setWidth(width)
        pen.setColor(QColor(color))
        painter.setPen(pen)
        painter.drawPoint(x, y)
        painter.end()
        self.update_map_image()

    def update_map_image(self):
        # update() и repaint() у self.mapLabel работают хуёво (не работают), поэтому постоянно заменяем pixmap
        self.mapLabel.setPixmap(self.mapPixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindowUI()
    mainWindow.show()
    sys.exit(app.exec_())
