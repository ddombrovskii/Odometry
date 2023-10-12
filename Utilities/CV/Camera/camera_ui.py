from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QLabel, QLineEdit, QPushButton
from Utilities.CV.Camera.image_widget import ImageWidget
from Utilities.CV import Camera
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from typing import Union
import cv2
import sys


class TextInputForm(QMainWindow):
    def __init__(self, callback_func, frame_title, field_tite):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(320, 140))
        self.setWindowTitle(frame_title)

        self.nameLabel = QLabel(self)
        self.nameLabel.setText(f'{field_tite}:')
        self.line = QLineEdit(self)

        self.line.move(80, 20)
        self.line.resize(200, 32)
        self.nameLabel.move(20, 20)

        pybutton = QPushButton('OK', self)
        pybutton.clicked.connect(lambda v: self.parse_input_data(callback_func))
        pybutton.resize(200, 32)
        pybutton.move(80, 60)

    def parse_input_data(self, callback_func):
        callback_func(self.line.text())
        self.destroy()


class CameraIU(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera_cv: Union[None, Camera] = None
        self._camera_thread = None
        self.setWindowTitle('Camera CV')
        self.setWindowIcon(QIcon('./assets/editor.png'))
        self.setGeometry(100, 100, 500, 300)
        self._build_menu_bar()
        self._image = ImageWidget(parent=self)
        self.setCentralWidget(self._image)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Camera status :: disconnected')
        timer_update = QTimer(self)
        timer_update.setInterval(30)  # period, in milliseconds
        timer_update.timeout.connect(self.update_image)
        timer_update.start()
        self.show()

    def _build_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        mode_menu = menu_bar.addMenu('&Modes')
        edit_menu = menu_bar.addMenu('&Settings')
        help_menu = menu_bar.addMenu('&Help')
        file_menu.addAction('Connect', lambda: self._connect_camera())
        file_menu.addAction('Connect to port', lambda: self._connect_camera_to_port())
        file_menu.addAction('Disconnect', lambda: self._disconnect_camera())
        file_menu.addAction('Exit', lambda: self._exit_app())

        mode_menu.addAction('SaveFrame', lambda: self._save_frame())
        mode_menu.addAction('RecordFrames', lambda: self._records_frames())
        mode_menu.addAction('RecordVideo', lambda: self._records_video())
        mode_menu.addAction('Stop', lambda: self._stop_modes())

    def _save_frame(self):
        if self.camera_available:
            self._camera_cv.save_frame()

    def _records_frames(self):
        if self.camera_available:
            self._camera_cv.record_frames()

    def _records_video(self):
        if self.camera_available:
            self._camera_cv.record_video()

    def _stop_modes(self):
        if self.camera_available:
            self._camera_cv.stop_all()

    def _connect_camera_to_port(self):
        TextInputForm(lambda message: self._connect_camera(message), "Assign port index", "Port №").show()

    def _connect_camera(self, port_id: int = 0):
        try:
            if self._camera_cv is None:
                self._camera_cv = Camera(int(port_id))
                self._camera_cv.run_in_separated_thread()
                self.status_bar.showMessage(f'Camera status :: connected to camera port {self._camera_cv.camera_cv}')
        except ValueError | cv2.error as _:
            self.status_bar.showMessage(f'Camera status :: failed to establish port connection {port_id}')

    def _disconnect_camera(self):
        if self._camera_cv is not None:
            self._camera_cv.camera_cv.close_camera()
            self._camera_cv = None
            self.status_bar.showMessage('Camera status :: disconnected')

    def _exit_app(self):
        self._disconnect_camera()
        self.close()

    @property
    def camera_available(self) -> bool:
        if self._camera_cv is None:
            return False
        return self._camera_cv.is_open

    def update_image(self) -> None:
        if self.camera_available:
            try:
                self._image.setPixmap(self._camera_cv.camera_cv.undistorted_frame)
            except Exception as _:
                self.status_bar.showMessage('Camera status :: failed to read frame')

    def closeEvent(self, a0) -> None:
        self._disconnect_camera()

    # def destroy(self, destroyWindow: bool = ..., destroySubWindows: bool = ...) -> None:
    #     self._disconnect_camera()
    #     super().destroy(destroyWindow, destroySubWindows)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraIU()
    sys.exit(app.exec())
