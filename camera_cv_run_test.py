from Utilities.CV import Camera, CameraIU
from PyQt5.QtWidgets import QApplication
import sys


def run_camera_using_cv():
    c = Camera()
    c.run_cv()


def run_camera_using_qt():
    app = QApplication(sys.argv)
    window = CameraIU()
    sys.exit(app.exec())


if __name__ == '__main__':
    # run_camera_using_cv()
    run_camera_using_qt()
