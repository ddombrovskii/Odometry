from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QComboBox, QGroupBox, QHBoxLayout
from qt_widgets_utils import buttons_group, init_drop_down, init_vect_3, init_text_field, image_widget, init_mat_4
from Utilities.Geometry import Vector3


class PathSegmentWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        # TODO уменьшить расстояние между элементами по высоте до минимума
        # TODO уменьшить полную ширину до минимума
        super(PathSegmentWidget, self).__init__(parent=parent)

        self._layout: QVBoxLayout | None = None

        self._path_name_label: QLabel | None = None
        self._points_count_label: QLabel | None = None

        self._path_raw_length: QLabel | None = None
        self._path_length: QLabel | None = None

        self._start_x: QLineEdit | None = None
        self._start_y: QLineEdit | None = None
        self._start_z: QLineEdit | None = None

        self._end_x: QLineEdit | None = None
        self._end_y: QLineEdit | None = None
        self._end_z: QLineEdit | None = None

        self._decimate_drop_down: QComboBox | None = None
        self._smoothing_drop_down: QComboBox | None = None

        self._go_to_start_btn: QPushButton | None = None
        self._go_to_end_btn: QPushButton | None = None

        self._start_btn: QPushButton | None = None
        self._stop_btn: QPushButton | None = None
        self._reverse_btn: QPushButton | None = None

        try:
            self._init_layouts()
        except RuntimeError as _:
            ...

    @property
    def main_layout(self) -> QVBoxLayout:
        """
        Лейаут с элементами
        """
        return self._layout

    @property
    def main_container(self) -> QWidget:
        """
        Контейнер с элементами
        """
        return self

    @property
    def start_pt(self) -> Vector3:
        return Vector3(float(self._start_x.text()), float(self._start_y.text()), float(self._start_z.text()))

    @start_pt.setter
    def start_pt(self, v: Vector3) -> None:
        self._set_start_pt(*v)

    @property
    def end_pt(self) -> Vector3:
        return Vector3(float(self._end_x.text()), float(self._end_y.text()), float(self._end_z.text()))

    @end_pt.setter
    def end_pt(self, v: Vector3) -> None:
        self._set_end_pt(*v)

    @property
    def points_count(self) -> int:
        return int(self._points_count_label.text())

    @points_count.setter
    def points_count(self, v: int) -> None:
        self._points_count_label.setText(str(v))

    @property
    def path_length(self) -> float:
        return float(self._path_length.text())

    @path_length.setter
    def path_length(self, v: float) -> None:
        self._set_path_length(v)

    @property
    def path_raw_length(self) -> float:
        return float(self._path_length.text())

    @path_raw_length.setter
    def path_raw_length(self, v: float) -> None:
        self._set_path_raw_length(v)

    @property
    def path_name(self) -> str:
        return self._path_name_label.text()

    @path_name.setter
    def path_name(self, value: str) -> None:
        self._path_name_label.setText(value)

    def _init_layouts(self):
        """
        #####################################
        ###     COMMON PATH INFO GROUP    ###
        #####################################
        """
        self._layout = QVBoxLayout()
        common_group = QGroupBox(self)
        common_group.setTitle("Общая информация о сегменте пути")
        common_layout = QVBoxLayout()
        common_layout.setContentsMargins(0, 0, 0, 0)
        # common_group.setStyleSheet("border:1px solid rgb(41, 41, 41); ")

        container, self._path_name_label = init_text_field(common_group, label_str="Имя")
        common_layout.addWidget(container)

        container, self._points_count_label = init_text_field(common_group, label_str="Количество точек")
        common_layout.addWidget(container)

        container, self._path_raw_length = init_text_field(common_group, label_str="Длина(до обработки)")
        common_layout.addWidget(container)

        container, self._path_length = init_text_field(common_group, label_str="Длина(после обработки)")
        common_layout.addWidget(container)
        common_group.setLayout(common_layout)
        self._layout.addWidget(common_group)
        """
        #####################################
        ###     PATH BOUNDS INFO GROUP    ###
        #####################################
        """
        group = QGroupBox(self)
        group.setTitle("Path bounds")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        container, self._start_x, self._start_y, self._start_z = init_vect_3(group, label_str="Начало",
                                                                             vert=True, as_group=False)
        layout.addWidget(container)

        container, self._end_x, self._end_y, self._end_z = init_vect_3(group, label_str="Конец",
                                                                       vert=True, as_group=False)
        layout.addWidget(container)
        group.setLayout(layout)
        self._layout.addWidget(group)
        """
        #####################################
        ###     PATH POST PROCESS GROUP   ###
        #####################################
        """
        path_post_process_group = QGroupBox(self)
        path_post_process_group.setTitle("Параметры пост обработки пути")
        path_post_process_layout = QVBoxLayout()
        path_post_process_layout.setContentsMargins(0, 0, 0, 0)
        container, self._decimate_drop_down = init_drop_down(path_post_process_group, label_str="Децимирование")
        path_post_process_layout.addWidget(container)

        container, self._smoothing_drop_down = init_drop_down(path_post_process_group, label_str="Сглаживание")
        path_post_process_layout.addWidget(container)
        path_post_process_group.setLayout(path_post_process_layout)
        self._layout.addWidget(path_post_process_group)
        """
        #####################################
        ###      PATH MOVEMENT GROUP      ###
        #####################################
        """
        path_movement_group = QGroupBox(self)
        path_movement_group.setTitle("Управление движением по сегменту")
        path_movement_layout = QVBoxLayout()
        path_movement_layout.setContentsMargins(0, 0, 0, 0)

        container, direction_buttons = buttons_group(path_movement_group, label_str="",
                                                     buttons_str=["иди вперёд", "иди назад"])
        self._go_to_start_btn = direction_buttons[0]
        self._go_to_end_btn = direction_buttons[1]
        path_movement_layout.addWidget(container)

        container, state_buttons = buttons_group(path_movement_group, label_str="",
                                                 buttons_str=["иди", "стой", "обратно"])
        self._start_btn = state_buttons[0]
        self._stop_btn = state_buttons[1]
        self._reverse_btn = state_buttons[2]
        path_movement_layout.addWidget(container)
        path_movement_group.setLayout(path_movement_layout)
        self._layout.addWidget(path_movement_group)
        self.setLayout(self._layout)

    def _set_path_name(self, name: str):
        self._path_name_label.setText(name)

    def _set_points_count(self, name: str):
        self._points_count_label.setText(name)

    def _set_path_raw_length(self, value: float):
        self._path_raw_length.setText(str(value))

    def _set_path_length(self, value: float):
        self._path_length.setText(str(value))

    def _set_start_pt(self, start_x: float, start_y: float, start_z: float):
        self._start_x.setText(str(start_x))
        self._start_y.setText(str(start_y))
        self._start_z.setText(str(start_z))

    def _set_end_pt(self, end_x: float, end_y: float, end_z: float):
        self._end_x.setText(str(end_x))
        self._end_y.setText(str(end_y))
        self._end_z.setText(str(end_z))

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
