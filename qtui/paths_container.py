from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма

from PyQt5.QtCore import Qt, pyqtSlot, pyqtBoundSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QGridLayout, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QComboBox, QScrollArea, QDialog, QFrame
import sys
from typing import Tuple, List

class PathsContainer(QWidget):
    """
    Класс контейнер для элементов. Позволяет добавить элементы или удалить их.
    TODO Добавить возможность вертикального скролинга
    """

    def __init__(self, widget: QFrame, width: int = 300, height: int = 600, window_name: str = "MainWindow"):
        super(PathsContainer, self).__init__()
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert isinstance(window_name, str)
        self.init_parameters(widget)

    def init_parameters(self, widget: QFrame):
        # self._root.setFixedSize(300, 600)
        # self._root.setMinimumWidth(300)
        # self._root.setMinimumHeight(600)
        # self._root.setWindowTitle(window_name)
        self._root = QVBoxLayout(widget)
        self._widgets = {}

    @property
    def container(self) -> QVBoxLayout:
        """
        Контейнер с элементами
        """
        return self._root

    def register_element(self, element: QWidget) -> int:
        """
        Привязвыет элементы интерфейса к родителю
        """
        unique_id = id(element)
        if id(element) in self._widgets:
            return -1
        self._widgets.update({unique_id: element})
        element.setParent(self)
        return unique_id

    def unregister_element(self, element: QWidget | int) -> bool:
        """
        Отвязывает и удаляет элементы интерфейса от родителя
        """
        if isinstance(element, QWidget):
            unique_id = id(element)
        elif isinstance(element, int):
            unique_id = element
        else:
            raise RuntimeError("Unsupported widget type")

        if id(element) in self._widgets:
            return False
        self._widgets[unique_id].deleteLater()
        del self._widgets[unique_id]
        return True

class PathSegmentWidget(QWidget):
    @staticmethod
    def init_vect_2(parent: QVBoxLayout, label_str: str = "label", x_str: str = "X",
                    y_str: str = "Y") -> Tuple[QWidget, QLineEdit, QLineEdit]:
        container = QWidget()  # контейнер с вертикальным размещением
        label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")
        layout = QVBoxLayout()
        vect_container = QWidget()  # контейнер с горизонтальным размещением
        # container.move(10, 100) # так не нужно делать.
        # нужно использовать QVBoxLayout для вертикального размещения компонентов
        # в родителе или QHBoxLayout для горизонтального
        # X - coordinate
        label_x = QLabel(f"{x_str} :")
        input_x = QLineEdit()
        input_x = style_for_qlineedit(input_x)

        # Y - coordinate
        label_y = QLabel(f"{y_str} :")
        input_y = QLineEdit()
        input_y = style_for_qlineedit(input_y)

        vect_layout = QHBoxLayout()
        vect_layout.addWidget(label_x)
        vect_layout.addWidget(input_x)

        vect_layout.addWidget(label_y)
        vect_layout.addWidget(input_y)

        vect_container.setLayout(vect_layout)

        if label is not None:
            layout.addWidget(label)
        layout.addWidget(vect_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, input_x, input_y

    @staticmethod
    def init_vect_3(parent: QVBoxLayout, label_str: str = "label", x_str: str = "X",
                    y_str: str = "Y", z_str: str = "Z") -> Tuple[QWidget, QLineEdit, QLineEdit, QLineEdit]:

        container = QWidget()  # контейнер с вертикальным размещением
        label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")
        layout = QVBoxLayout()

        vect_container = QWidget()  # контейнер с горизонтальным размещением
        # X - coordinate
        label_x = QLabel(f"{x_str} :")
        input_x = QLineEdit()
        input_x = style_for_qlineedit(input_x)

        # Y - coordinate
        label_y = QLabel(f"{y_str} :")
        input_y = QLineEdit()
        input_y = style_for_qlineedit(input_y)

        # Z - coordinate
        label_z = QLabel(f"{z_str} :")
        input_z = QLineEdit()
        input_z = style_for_qlineedit(input_z)

        vect_layout = QHBoxLayout()
        vect_layout.addWidget(label_x)
        vect_layout.addWidget(input_x)

        vect_layout.addWidget(label_y)
        vect_layout.addWidget(input_y)

        vect_layout.addWidget(label_z)
        vect_layout.addWidget(input_z)

        vect_container.setLayout(vect_layout)

        if label is not None:
            layout.addWidget(label)
        layout.addWidget(vect_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, input_x, input_y, input_z

    @staticmethod
    def init_vect_4(parent: QVBoxLayout, label_str: str = "label", x_str: str = "\"X\"",
                    y_str: str = "\"Y\"", z_str: str = "\"Z\"", w_str: str = "\"W\"") -> \
            Tuple[QWidget, QLineEdit, QLineEdit, QLineEdit, QLineEdit]:
        container = QWidget()  # контейнер с вертикальным размещением
        label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        layout = QVBoxLayout()
        vect_container = QWidget()  # контейнер с горизонтальным размещением
        # X - coordinate
        label_x = QLabel(f"{x_str} :")
        input_x = QLineEdit()
        input_x = style_for_qlineedit(input_x)
        input_x.setText("0.0")

        # Y - coordinate
        label_y = QLabel(f"{y_str} :")
        input_y = QLineEdit()
        input_y = style_for_qlineedit(input_y)
        input_y.setText("0.0")

        # Z - coordinate
        label_z = QLabel(f"{z_str} :")
        input_z = QLineEdit()
        input_z = style_for_qlineedit(input_z)
        input_z.setText("0.0")

        # W - coordinate
        label_w = QLabel(f"{w_str} :")
        input_w = QLineEdit()
        input_w = style_for_qlineedit(input_w)
        input_w.setText("0.0")

        vect_layout = QHBoxLayout()
        vect_layout.addWidget(label_x)
        vect_layout.addWidget(input_x)

        vect_layout.addWidget(label_y)
        vect_layout.addWidget(input_y)

        vect_layout.addWidget(label_z)
        vect_layout.addWidget(input_z)

        vect_layout.addWidget(label_w)
        vect_layout.addWidget(input_w)
        vect_container.setLayout(vect_layout)
        if label is not None:
            layout.addWidget(label)
        layout.addWidget(vect_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, input_x, input_y, input_z, input_w

    @staticmethod
    def init_mat_2(parent: QVBoxLayout, label_str: str = "label") -> [QWidget, List[QLineEdit]]:
        container = QWidget()  # контейнер с вертикальным размещением
        label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        layout = QVBoxLayout()

        mat_container = QWidget()
        rows_layout = QVBoxLayout()

        row1, m00, m01 = PathSegmentWidget.init_vect_2(parent, label_str="", x_str="\"M00\"", y_str="\"M01\"")
        rows_layout.addWidget(row1)

        row2, m10, m11 = PathSegmentWidget.init_vect_2(parent, label_str="", x_str="\"M10\"", y_str="\"M11\"")
        rows_layout.addWidget(row2)

        mat_container.setLayout(rows_layout)
        if label is not None:
            layout.addWidget(label)
        layout.addWidget(mat_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, [m00, m01, m10, m11]

    @staticmethod
    def init_mat_3(parent: QVBoxLayout, label_str: str = "label") -> [QWidget, List[QLineEdit]]:
        container = QWidget()  # контейнер с вертикальным размещением
        label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        layout = QVBoxLayout()

        mat_container = QWidget()
        rows_layout = QVBoxLayout()

        row1, m00, m01, m02 = PathSegmentWidget.init_vect_3(parent, label_str="",
                                                            x_str="\"M00\"", y_str="\"M01\"", z_str="\"M02\"")
        rows_layout.addWidget(row1)

        row2, m10, m11, m12 = PathSegmentWidget.init_vect_3(parent, label_str="",
                                                            x_str="\"M10\"", y_str="\"M11\"", z_str="\"M12\"")
        rows_layout.addWidget(row2)

        row3, m20, m21, m22 = PathSegmentWidget.init_vect_3(parent, label_str="",
                                                            x_str="\"M20\"", y_str="\"M21\"", z_str="\"M22\"")
        rows_layout.addWidget(row3)

        mat_container.setLayout(rows_layout)
        if label is not None:
            layout.addWidget(label)
        layout.addWidget(mat_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, [m00, m01, m02, m10, m11, m12, m20, m21, m22]

    @staticmethod
    def init_mat_4(parent: QVBoxLayout, label_str: str = "label") -> [QWidget, List[QLineEdit]]:
        container = QWidget()  # контейнер с вертикальным размещением
        label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        layout = QVBoxLayout()

        mat_container = QWidget()
        rows_layout = QVBoxLayout()

        row1, m00, m01, m02, m03 = PathSegmentWidget.init_vect_4(parent, label_str="",
                                                                 x_str="\"M00\"", y_str="\"M01\"",
                                                                 z_str="\"M02\"", w_str="\"M03\"")
        rows_layout.addWidget(row1)

        row2, m10, m11, m12, m13 = PathSegmentWidget.init_vect_4(parent, label_str="",
                                                                 x_str="\"M10\"", y_str="\"M11\"",
                                                                 z_str="\"M12\"", w_str="\"M13\"")
        rows_layout.addWidget(row2)

        row3, m20, m21, m22, m23 = PathSegmentWidget.init_vect_4(parent, label_str="",
                                                                 x_str="\"M20\"", y_str="\"M21\"",
                                                                 z_str="\"M22\"", w_str="\"M23\"")
        rows_layout.addWidget(row3)

        row4, m30, m31, m32, m33 = PathSegmentWidget.init_vect_4(parent, label_str="",
                                                                 x_str="\"M30\"", y_str="\"M31\"",
                                                                 z_str="\"M32\"", w_str="\"M33\"")
        rows_layout.addWidget(row4)

        mat_container.setLayout(rows_layout)
        if label is not None:
            layout.addWidget(label)
        layout.addWidget(mat_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, [m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33]

    @staticmethod
    def init_text_field(parent: QVBoxLayout, label_str: str = "text field",
                        start_value: str = "nothing") -> Tuple[QWidget, QLabel]:
        container = QWidget()  # контейнер с горизонтальным размещением
        label_name = QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        label_text = QLabel(f"{start_value}")  # поле которое можно поменять из вне
        layout = QHBoxLayout()
        layout.addWidget(label_name)
        layout.addWidget(label_text)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, label_text

    @staticmethod
    def init_drop_down(parent: QVBoxLayout, label_str: str = "drop down",
                       values: List[str] | None = None) -> Tuple[QWidget, QComboBox]:
        container = QWidget()  # контейнер с горизонтальным размещением
        label = QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        drop_down = QComboBox()
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(drop_down)
        container.setLayout(layout)
        drop_down.addItems(["item 1", "item 2", "item 3"] if values is None else values)
        parent.addWidget(container)
        return container, drop_down

    @staticmethod
    def buttons_group(parent: QVBoxLayout, label_str: str = "buttons group",
                      buttons_str: List[str] | None = None, vert: bool = False) -> Tuple[QWidget, List[QPushButton]]:
        container = QWidget()  # контейнер с вертикальным размещением
        label = QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
        layout = QVBoxLayout()
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout() if vert else QHBoxLayout()
        buttons = [QPushButton(name) for name in ("btn1", "btn2", "btn3")] if buttons_str is None else \
            [QPushButton(name) for name in buttons_str]
        for b in buttons:
            buttons_layout.addWidget(b)
        buttons_container.setLayout(buttons_layout)
        layout.addWidget(label)
        layout.addWidget(buttons_container)
        container.setLayout(layout)
        parent.addWidget(container)
        return container, buttons

    def __init__(self, parent: QVBoxLayout):
        super(PathSegmentWidget, self).__init__()
        
        self._layout: QVBoxLayout | None = None        
        
        self._path_name_label:   QLabel | None = None 
        self._points_count_label: QLabel | None = None
        
        self._start_x: QLineEdit | None = None
        self._start_y: QLineEdit | None = None
        self._start_z: QLineEdit | None = None
        
        self._end_x: QLineEdit | None = None
        self._end_y: QLineEdit | None = None
        self._end_z: QLineEdit | None = None
        
        self._decimate_drop_down:  QComboBox | None = None
        self._smoothing_drop_down: QComboBox | None = None
        
        self._go_to_start_btn: QPushButton | None = None
        self._go_to_end_btn:   QPushButton | None = None
        
        self._start_btn:   QPushButton | None = None
        self._stop_btn:    QPushButton | None = None
        self._reverse_btn: QPushButton | None = None
    
        try:
            self._init_layouts(parent)
        except RuntimeError as _:
            ...

    @property
    def vertical_container(self) -> QVBoxLayout:
        """
        Контейнер с элементами
        """
        return self._layout

    def _init_layouts(self, parent: QVBoxLayout):
        # реализовать
        self._layout = parent
        
        container, path_name_label = PathSegmentWidget.init_text_field(parent, label_str="Path 0")
        self._path_name_label = path_name_label
        self._layout.addWidget(container)

        container, points_count_label = PathSegmentWidget.init_text_field(parent, label_str="Path points count")
        self._points_count_label = points_count_label
        self._layout.addWidget(container)

        container, start_x, start_y, start_z = PathSegmentWidget.init_vect_3(parent, label_str="Start Point")
        self._start_x = start_x
        self._start_y = start_y
        self._start_z = start_z
        self._layout.addWidget(container)

        container, end_x, end_y, end_z = PathSegmentWidget.init_vect_3(parent, label_str="End Point")
        self._end_x = end_x
        self._end_y = end_y
        self._end_z = end_z
        self._layout.addWidget(container)

        container, decimate_drop_down = PathSegmentWidget.init_drop_down(parent, label_str="Decimate")
        self._decimate_drop_down = decimate_drop_down
        self._layout.addWidget(container)

        container, smoothing_drop_down = PathSegmentWidget.init_drop_down(parent, label_str="Path smoothing")
        self._smoothing_drop_down = smoothing_drop_down
        self._layout.addWidget(container)

        container, direction_buttons = PathSegmentWidget.buttons_group(parent, label_str="Movment direction",
                                                                       buttons_str=["go to start", "go to end"])

        self._go_to_start_btn = direction_buttons[0]
        self._go_to_end_btn   = direction_buttons[1]

        self._layout.addWidget(container)

        container, state_buttons = PathSegmentWidget.buttons_group(parent, label_str="Movment state",
                                                                   buttons_str=["start", "pause", "reverse"])

        self._start_btn   = state_buttons[0]
        self._stop_btn    = state_buttons[1]
        self._reverse_btn = state_buttons[2]
        self._layout.addWidget(container)

    def _set_path_name(self, name: str):
        self._path_name_label = name

    def _set_points_count(self, name: str):
        self._points_count_label = name

    def _set_start_pt(self, start_x: float, start_y: float, start_z: float):
        self._start_x = start_x
        self._start_y = start_y
        self._start_z = start_z

    def _set_end_pt(self, end_x: float, end_y: float, end_z: float):
        self._end_x = end_x
        self._end_y = end_y
        self._end_z = end_z

    def _on_decimate_value_changed(self):
        ...

    def _on_smooth_value_changed(self):
        ...

    def _on_go_to_start_clicked(self):
        ...

    def _on_go_to_end_clicked(self):
        ...

    def _on_go_clicked(self):
        ...

    def _on_stop_clicked(self):
        ...

def style_for_qlineedit(qlineedit: QLineEdit):
    qlineedit.setEnabled(False)
    qlineedit.setStyleSheet("color : black;}")
    qlineedit.setText("0.0")
    qlineedit.setAlignment(Qt.AlignCenter)
    qlineedit.setMinimumWidth(50)

    return qlineedit


def ui_example(widget) -> QWidget:
    # Инициализация виджета
    # Начиная отсюда

    # root = QWidget()
    # root.resize(200, 600)
    # root.setMinimumWidth(200)
    # root.setMinimumHeight(600)
    # root.setWindowTitle("Widget")


    # layout = QVBoxLayout()
    #
    # # Начиная отсюда
    # container, path_name_label = PathSegmentWidget.init_text_field(root, label_str="Path 0")
    # layout.addWidget(container)
    #
    # container, points_count_label = PathSegmentWidget.init_text_field(root, label_str="Path points count")
    # layout.addWidget(container)
    #
    # container, start_x, start_y, start_z = PathSegmentWidget.init_vect_3(root, label_str="Start Point")
    # layout.addWidget(container)
    #
    # container, end_x, end_y, end_z = PathSegmentWidget.init_vect_3(root, label_str="End Point")
    # layout.addWidget(container)
    #
    # container, decimate_drop_down = PathSegmentWidget.init_drop_down(root, label_str="Decimate")
    # layout.addWidget(container)
    #
    # container, smoothing_drop_down = PathSegmentWidget.init_drop_down(root, label_str="Path smoothing")
    # layout.addWidget(container)
    #
    # container, direction_buttons = PathSegmentWidget.buttons_group(root, label_str="Movment direction",
    #                                                                buttons_str=["go to start", "go to end"])
    # layout.addWidget(container)
    #
    # container, state_buttons = PathSegmentWidget.buttons_group(root, label_str="Movment state",
    #                                                            buttons_str=["start", "pause", "reverse"])
    # layout.addWidget(container)

    path_container = PathsContainer(widget)
    path_segment_widget = PathSegmentWidget(path_container.container)

    # return path_container.container


if __name__ == "__main__":
    # НИКАКИХ ФУНКЦИЙ ПО ИНИЦИАЛИЗАЦИИ ВНУТРИ МЕЙН!
    # ТОЛЬКО ОСНОВНАЯ ТОЧКА ВХОДА!
    app = QApplication(sys.argv)
    root = ui_example()
    root.show()
    sys.exit(app.exec_())
