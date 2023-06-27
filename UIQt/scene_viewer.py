from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication
from UIQt.scene_viewer_widget import SceneViewerWidget
from PyQt5.QtGui import QCloseEvent
from PyQt5 import QtCore
import sys


class SceneViewer(QWidget):
    def __init__(self):
        super(SceneViewer, self).__init__()  # call the init for the parent class
        self.resize(1000, 1000)
        self.setWindowTitle('Hello OpenGL App')
        self.glWidget: SceneViewerWidget = SceneViewerWidget(self)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.glWidget)
        self.setLayout(main_layout)
        timer_update = QtCore.QTimer(self)
        timer_update.setInterval(30)  # period, in milliseconds
        timer_update.timeout.connect(self.glWidget.updateGL)
        timer_update.start()
        timer_paint = QtCore.QTimer(self)
        timer_paint.setInterval(30)  # period, in milliseconds
        timer_paint.timeout.connect(self.glWidget.paintGL)
        timer_paint.start()
        self.closeEvent(QCloseEvent())

    def closeEvent(self, a0) -> None:
        self.glWidget.clean_up()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SceneViewer()
    window.show()
    sys.exit(app.exec_())
