from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from path_segment_widget import PathSegmentWidget
from paths_list_widget import PathsListWidget
from Utilities.Geometry import Vector3
import sys


def path_container_example(parent: QWidget = None) -> PathSegmentWidget:
    container = PathSegmentWidget(parent)
    container.start_pt = Vector3(1, 2, 3)
    container.end_pt = Vector3(3, 2, 1)
    container.points_count = 123
    container.path_raw_length = 0.987
    container.path_length = 0.1987
    container.path_name = "this is my first path"
    return container


def path_container_test():
    app = QApplication(sys.argv)
    container = path_container_example()
    container.show()
    sys.exit(app.exec_())


def path_list_container_test():
    app = QApplication(sys.argv)
    # win = QMainWindow()
    # win.setWindowTitle("Path segments")
    list_of_path = PathsListWidget()  # (win)
    list_of_path.register_element(path_container_example(list_of_path.list_widget))
    list_of_path.register_element(path_container_example(list_of_path.list_widget))
    list_of_path.register_element(path_container_example(list_of_path.list_widget))
    list_of_path.show()
    # path_container = path_container_example()
    # list_of_path.adjustSize()
    # win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # НИКАКИХ ФУНКЦИЙ ПО ИНИЦИАЛИЗАЦИИ ВНУТРИ МЕЙН!
    # ТОЛЬКО ОСНОВНАЯ ТОЧКА ВХОДА!
    path_container_test()
    # path_list_container_test()

