from PyQt5.uic.properties import QtGui

from UIQt.GLUtilities.gl_shader import Shader
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.scene_viewer_widget import SceneViewerWidget
from UIQt.GLUtilities.triangle_mesh import create_plane
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from PyQt5 import QtCore, QtWidgets
from Utilities import Transform, Matrix4
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication
import sys
from PyQt5.QtGui import QColor, QSurfaceFormat, QCloseEvent


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()  # call the init for the parent class
        self.resize(300, 300)
        self.setWindowTitle('Hello OpenGL App')
        self.glWidget: SceneViewerWidget = SceneViewerWidget(self)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        timer_update = QtCore.QTimer(self)
        timer_update.setInterval(20)  # period, in milliseconds
        timer_update.timeout.connect(self.glWidget.updateGL)
        timer_update.start()
        timer_paint = QtCore.QTimer(self)
        timer_paint.setInterval(33)  # period, in milliseconds
        timer_paint.timeout.connect(self.glWidget.paintGL)
        timer_paint.start()

        self.closeEvent(QCloseEvent())

    def closeEvent(self, a0) -> None:
        self.glWidget.clean_up()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
