from TexturizedCubeWidget import TexturizedCubeWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QSurfaceFormat
import sys


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        clearColor = QColor()
        # clearColor.setHsv(((i * Window.NumColumns) + j) * 255 / (Window.NumRows * Window.NumColumns - 1), 255, 63)

        self.glWidget = TexturizedCubeWidget()
        self.glWidget.setClearColor(clearColor)

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()

        self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
        self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
        self.ySlider.valueChanged.connect(self.glWidget.setYRotation)
        self.glWidget.yRotationChanged.connect(self.ySlider.setValue)
        self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
        self.glWidget.zRotationChanged.connect(self.zSlider.setValue)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        self.setLayout(mainLayout)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        self.setWindowTitle("Texturized Cube")

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider


if __name__ == '__main__':
    app = QApplication(sys.argv)

    format = QSurfaceFormat()
    format.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(format)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
