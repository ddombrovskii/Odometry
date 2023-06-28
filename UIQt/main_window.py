from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QFileDialog, QTabWidget

from UIQt.GLUtilities import gl_globals
from UIQt.GLUtilities.gl_scene import merge_scene
from UIQt.Scripts.Functionality.path_create_behaviour import PathCreateBehaviour
from UIQt.Scripts.Functionality.swich_view_behavior import SwitchViewBehaviour
from UIQt.Scripts.map_renderers import WeightsMapRenderer
from UIQt.scene_viewer_widget import SceneViewerWidget
from Utilities.Geometry import Vector2
from point_widget import PointWidget
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt, QTimer
from serial import SerialException
from typing import List
from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма
import serial
import sys
import os
UART_START_MESSAGE = b'$#'
UART_END_MESSAGE = b'#$'


def send_to_uart(data: List[Vector2], port="COM5"):
    try:
        serial_port = serial.Serial(port, baudrate=115200, timeout=1, bytesize=8, stopbits=serial.STOPBITS_ONE)
        serial_port.write(UART_START_MESSAGE)
        data = bytes("|".join(f"{v.x:.3f},{v.y:.3f}" for v in data), "utf-8")
        serial_port.write(data)
        serial_port.write(UART_END_MESSAGE)
    except SerialException as ex:
        print(ex.args)


class MainWindowUI(QMainWindow):
    def __init__(self):
        super(MainWindowUI, self).__init__()
        uic.loadUi("./UI/MainWindow.ui", self)
        self._gl_widget: SceneViewerWidget | None = None
        self._way_points: List[Vector2] = []
        self._way_points_widgets: List[PointWidget] = []
        self._path_builder: PathCreateBehaviour | None = None
        self._projection_switcher: SwitchViewBehaviour | None = None

        self._init_layouts()
        self._init_buttons()
        self._setup_update_rate()
        self.closeEvent(QCloseEvent())

    def _start_movement(self):
        if self._path_builder is None:
            return
        if len(self._path_builder.path_sections) == 0:
            return
        path = self._path_builder.path_sections[-1]
        send_to_uart(path)

    def _init_layouts(self):
        # left tab
        leftTabWidget: QTabWidget = self.findChild(QTabWidget, "leftTabWidget")
        leftTabWidget.setCurrentIndex(0)  # делает вкладку "точки" активным

        # left tab (точки)
        self.points_layout: QVBoxLayout = self.findChild(QVBoxLayout, "pointsVLayout")
        self.points_layout.setAlignment(Qt.AlignTop)  # устанавливаю добавление точек на верх списка

        # left tab (ракурсы)
        angles_layout: QVBoxLayout = self.findChild(QVBoxLayout, "anglesVLayout")
        angles_layout.setAlignment(Qt.AlignTop)

        # right tab
        # если сделать "карта" открытым табом по умолчанию, то приложение вылетит
        rightTabWidget: QTabWidget = self.findChild(QTabWidget, "rightTabWidget")
        rightTabWidget.setCurrentIndex(0)
        

        # right tab (3D)
        mapLayout = self.findChild(QVBoxLayout, "mapTabVLayout")
        self._gl_widget: SceneViewerWidget = SceneViewerWidget(self)
        self._projection_switcher = SwitchViewBehaviour(self._gl_widget.scene_gl)
        mapLayout.insertWidget(1, self._gl_widget)

    def _setup_update_rate(self):
        timer_update = QTimer(self)
        timer_update.setInterval(16)  # period, in milliseconds
        timer_update.timeout.connect(self._gl_widget.updateGL)
        timer_update.start()
        timer_paint = QTimer(self)
        timer_paint.setInterval(16)  # period, in milliseconds
        timer_paint.timeout.connect(self._gl_widget.paintGL)
        timer_paint.start()

    def _init_buttons(self):
        # объявление кнопок в табе "карта"
        setup_path:       QPushButton = self.findChild(QPushButton, "setupPathPointBtn")
        start_movement:   QPushButton = self.findChild(QPushButton, "startMoveBtn")
        stop_movement:    QPushButton = self.findChild(QPushButton, "stopMoveBtn")
        perspective_prj:  QPushButton = self.findChild(QPushButton, "perspectiveProjectionBtn")
        orthographic_prj: QPushButton = self.findChild(QPushButton, "orthoProjectionBtn")
        add_view:         QPushButton = self.findChild(QPushButton, "addAngleBtn")
        delete_view:      QPushButton = self.findChild(QPushButton, "deleteAngleBtn")
        load_map:         QPushButton = self.findChild(QPushButton, "loadMapBtn")
        delete_map:       QPushButton = self.findChild(QPushButton, "deleteMapBtn")

        setup_path.      clicked.connect(lambda: self._path_setup_mode())
        start_movement.  clicked.connect(lambda: self._start_movement())
        orthographic_prj.clicked.connect(lambda: self._projection_switcher.switch_view())
        perspective_prj. clicked.connect(lambda: self._projection_switcher.switch_view())
        load_map.        clicked.connect(lambda: self.load_map())
        delete_map.      clicked.connect(lambda: self.clear_map())

    def _path_setup_mode(self):
        if self._path_builder is None:
            return
        self._path_builder.enabled = not self._path_builder.enabled

    def closeEvent(self, a0) -> None:
        self._gl_widget.clean_up()

    def clear_map(self):
        self._gl_widget.clear_scene()

    def load_map(self):
        directory = QFileDialog.getExistingDirectory(None, 'Open File', './')
        if directory == '':
            return

        merge_scene(self._gl_widget.scene_gl, directory)

        if not os.path.isdir(f"{directory}/Maps/"):
            os.mkdir(f"{directory}/Maps/")
        weights_renderer = WeightsMapRenderer(2048, 2048)
        weights_renderer.render_to_image(self._gl_widget.scene_gl, f"{directory}/Maps/weights_map.png")
        # self._path_builder = PathCreateBehaviour(self._gl_widget.scene_gl, directory, self.points_layout)
        # self._path_builder.enabled = False
        # self._gl_widget.register_behaviour(self._path_builder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindowUI()
    mainWindow.show()
    sys.exit(app.exec_())
