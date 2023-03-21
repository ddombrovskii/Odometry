from UIQt.GLUtilities.gl_shader import Shader
from UIQt.GLUtilities.gl_texture import TextureGL
from UIQt.scene_viewer_widget import SceneViewerWidget
from UIQt.GLUtilities.triangle_mesh import create_plane
from UIQt.GLUtilities.gl_material import MaterialGL
from UIQt.GLUtilities.gl_mesh import MeshGL
from PyQt5 import QtCore, QtWidgets
from Utilities import Transform
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication
import sys
from PyQt5.QtGui import QColor, QSurfaceFormat


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()  # call the init for the parent class
        self.resize(300, 300)
        self.setWindowTitle('Hello OpenGL App')
        self.glWidget: SceneViewerWidget = SceneViewerWidget(self)
        # self.initGUI()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
