from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox, QSizePolicy, \
    QGroupBox
from typing import Tuple, List
from PyQt5.QtCore import Qt

"""
#######################################
#      НИЧЕГО ЗДЕСЬ НЕ МЕНЯТЬ!!!      #
#######################################
"""


def style_for_q_line_edit(edit: QLineEdit):
    edit.setEnabled(False)
    edit.setStyleSheet("color : black;")
    # edit.setText("0.0")
    edit.setAlignment(Qt.AlignCenter)
    edit.setMinimumWidth(50)
    return edit


def init_immutable_text_field(parent: QWidget = None, label_str: str = "label", value_str: str = "label"):
    container = QWidget(parent)
    # container.setStyleSheet("border:0px")
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    text_field = QLineEdit()
    text_field = style_for_q_line_edit(text_field)
    text_field.setText(value_str)
    if len(label_str) != 0:
        label = QLabel(label_str)
        layout.addWidget(label)
    layout.addWidget(text_field)
    container.setLayout(layout)
    return container, text_field


def init_vect_2(parent: QWidget = None, label_str: str = "label", x_str: str = "X",
                y_str: str = "Y", vert: bool = False, as_group: bool = True) -> Tuple[QWidget, QLineEdit, QLineEdit]:
    container = QGroupBox(parent) if as_group else QWidget(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet("border:0px")
    layout         = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    # layout.addStretch(1)
    vect_container = QWidget()  # контейнер с горизонтальным размещением
    vect_layout    = QVBoxLayout() if vert else QHBoxLayout()
    vect_layout.setContentsMargins(0, 0, 0, 0)
    # X - coordinate
    container_x, text_x = init_immutable_text_field(label_str=f"{x_str} :", value_str="0.0")
    # Y - coordinate
    container_y, text_y = init_immutable_text_field(label_str=f"{y_str} :", value_str="0.0")
    vect_layout.addWidget(container_x)
    vect_layout.addWidget(container_y)
    vect_container.setLayout(vect_layout)
    if len(label_str) != 0:
        label = QLabel(f"{label_str} : ")
        layout.addWidget(label)
    layout.addWidget(vect_container)
    container.setLayout(layout)
    return container, text_x, text_y


def init_vect_3(parent: QWidget = None, label_str: str = "label", x_str: str = "X",
                y_str: str = "Y", z_str: str = "Z", vert: bool = False, as_group: bool = True) ->\
        Tuple[QWidget, QLineEdit, QLineEdit, QLineEdit]:
    container      = QGroupBox(parent) if as_group else QWidget(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet("border:0px")
    layout         = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    # layout.addStretch(1)
    vect_container = QWidget()  # контейнер с горизонтальным размещением
    vect_layout    = QVBoxLayout() if vert else QHBoxLayout()
    vect_layout.setContentsMargins(0, 0, 0, 0)
    # X - coordinate
    container_x, text_x = init_immutable_text_field(label_str=f"{x_str} :", value_str="0.0")
    # Y - coordinate
    container_y, text_y = init_immutable_text_field(label_str=f"{y_str} :", value_str="0.0")
    # Z - coordinate
    container_z, text_z = init_immutable_text_field(label_str=f"{z_str} :", value_str="0.0")
    vect_layout.addWidget(container_x)
    vect_layout.addWidget(container_y)
    vect_layout.addWidget(container_z)
    vect_container.setLayout(vect_layout)
    if len(label_str) != 0:
        label = QLabel(label_str)
        layout.addWidget(label)
    layout.addWidget(vect_container)
    container.setLayout(layout)
    return container, text_x, text_y, text_z


def init_vect_4(parent: QWidget = None, label_str: str = "label", x_str: str = "\"X\"",
                y_str: str = "\"Y\"", z_str: str = "\"Z\"", w_str: str = "\"W\"",
                vert: bool = False, as_group: bool = True) -> \
        Tuple[QWidget, QLineEdit, QLineEdit, QLineEdit, QLineEdit]:
    container = QGroupBox(parent) if as_group else QWidget(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet("border:0px")
    layout         = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    # layout.addStretch(1)
    vect_container = QWidget()  # контейнер с горизонтальным размещением
    vect_layout    = QVBoxLayout() if vert else QHBoxLayout()
    vect_layout.setContentsMargins(0, 0, 0, 0)
    # X - coordinate
    container_x, text_x = init_immutable_text_field(label_str=f"{x_str} :", value_str="0.0")
    # Y - coordinate
    container_y, text_y = init_immutable_text_field(label_str=f"{y_str} :", value_str="0.0")
    # Z - coordinate
    container_z, text_z = init_immutable_text_field(label_str=f"{z_str} :", value_str="0.0")
    # W - coordinate
    container_w, text_w = init_immutable_text_field(label_str=f"{w_str} :", value_str="0.0")
    vect_layout.addWidget(container_x)
    vect_layout.addWidget(container_y)
    vect_layout.addWidget(container_z)
    vect_layout.addWidget(container_w)
    vect_container.setLayout(vect_layout)
    if len(label_str) != 0:
        label = QLabel(f"{label_str} : ")
        layout.addWidget(label)
    layout.addWidget(vect_container)
    container.setLayout(layout)
    return container, text_x, text_y, text_z, text_w


def init_mat_2(parent: QWidget = None, label_str: str = "label") -> [QWidget, List[QLineEdit]]:
    container = QGroupBox(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet("border:0px")
    label = None if len(label_str) == 0 else QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch(1)
    mat_container = QWidget()
    rows_layout = QVBoxLayout()
    rows_layout.setContentsMargins(0, 0, 0, 0)

    # First row
    row1, m00, m01 = init_vect_2(mat_container, label_str="", x_str="\"M00\"", y_str="\"M01\"", as_group=False)
    rows_layout.addWidget(row1)
    # Second row
    row2, m10, m11 = init_vect_2(mat_container, label_str="", x_str="\"M10\"", y_str="\"M11\"", as_group=False)
    rows_layout.addWidget(row2)

    mat_container.setLayout(rows_layout)
    if label is not None:
        layout.addWidget(label)
    layout.addWidget(mat_container)
    container.setLayout(layout)
    return container, [m00, m01, m10, m11]


def init_mat_3(parent: QWidget = None, label_str: str = "label") -> [QWidget, List[QLineEdit]]:
    container = QGroupBox(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet("border:0px")
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch(1)
    mat_container = QWidget()
    rows_layout = QVBoxLayout()
    rows_layout.setContentsMargins(0, 0, 0, 0)

    # First row
    row1, m00, m01, m02 = \
        init_vect_3(mat_container, label_str="", x_str="\"M00\"", y_str="\"M01\"", z_str="\"M02\"", as_group=False)
    rows_layout.addWidget(row1)
    # Second row
    row2, m10, m11, m12 =\
        init_vect_3(mat_container, label_str="", x_str="\"M10\"", y_str="\"M11\"", z_str="\"M12\"", as_group=False)
    rows_layout.addWidget(row2)
    # Third row
    row3, m20, m21, m22 =\
        init_vect_3(mat_container, label_str="", x_str="\"M20\"", y_str="\"M21\"", z_str="\"M22\"", as_group=False)
    rows_layout.addWidget(row3)

    mat_container.setLayout(rows_layout)
    if len(label_str) != 0:
        label = QLabel(f"{label_str} : ")
        layout.addWidget(label)
    layout.addWidget(mat_container)
    container.setLayout(layout)
    return container, [m00, m01, m02, m10, m11, m12, m20, m21, m22]


def init_mat_4(parent: QWidget = None, label_str: str = "label") -> [QWidget, List[QLineEdit]]:
    container = QGroupBox(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet("border:0px")
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch(1)
    mat_container = QWidget()
    rows_layout = QVBoxLayout()
    rows_layout.setContentsMargins(0, 0, 0, 0)
    # First row
    row1, m00, m01, m02, m03 = init_vect_4(mat_container, label_str="",
                                           x_str="\"M00\"", y_str="\"M01\"",
                                           z_str="\"M02\"", w_str="\"M03\"", as_group=False)
    rows_layout.addWidget(row1)
    # Second row
    row2, m10, m11, m12, m13 = init_vect_4(mat_container, label_str="",
                                           x_str="\"M10\"", y_str="\"M11\"",
                                           z_str="\"M12\"", w_str="\"M13\"", as_group=False)
    rows_layout.addWidget(row2)
    # Third row
    row3, m20, m21, m22, m23 = init_vect_4(mat_container, label_str="",
                                           x_str="\"M20\"", y_str="\"M21\"",
                                           z_str="\"M22\"", w_str="\"M23\"", as_group=False)
    rows_layout.addWidget(row3)
    # Fourth row
    row4, m30, m31, m32, m33 = init_vect_4(mat_container, label_str="",
                                           x_str="\"M30\"", y_str="\"M31\"",
                                           z_str="\"M32\"", w_str="\"M33\"", as_group=False)
    rows_layout.addWidget(row4)

    mat_container.setLayout(rows_layout)
    if len(label_str) != 0:
        label = QLabel(f"{label_str} : ")
        layout.addWidget(label)
    layout.addWidget(mat_container)
    container.setLayout(layout)
    return container, [m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33]


def init_text_field(parent: QWidget = None, label_str: str = "text field",
                    start_value: str = "nothing") -> Tuple[QWidget, QLabel]:
    container = QWidget(parent)  # контейнер с горизонтальным размещением
    # container.setStyleSheet("border:0px;}")
    label_name = QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
    label_text = QLabel(f"{start_value}")  # поле которое можно поменять из вне
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(label_name)
    layout.addWidget(label_text)
    container.setLayout(layout)
    return container, label_text


def init_drop_down(parent: QWidget = None, label_str: str = "drop down",
                   values: List[str] | None = None) -> Tuple[QWidget, QComboBox]:
    container = QWidget(parent)  # контейнер с горизонтальным размещением
    # container.setStyleSheet("border:0px;}")
    label = QLabel(f"{label_str} : ")  # лейбл с заголовком элемента интерфейса
    drop_down = QComboBox()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(label)
    layout.addWidget(drop_down)
    container.setLayout(layout)
    drop_down.addItems(["item 1", "item 2", "item 3"] if values is None else values)
    return container, drop_down


def buttons_group(parent: QWidget = None, label_str: str = "buttons group",
                  buttons_str: List[str] | None = None, vert: bool = False) -> Tuple[QWidget, List[QPushButton]]:
    container = QWidget(parent)  # контейнер с вертикальным размещением
    # container.setStyleSheet(container.styleSheet() + "border:0px;")
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    buttons_container = QWidget()
    buttons_layout = QVBoxLayout() if vert else QHBoxLayout()
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons = [QPushButton(name) for name in ("btn1", "btn2", "btn3")] if buttons_str is None else \
        [QPushButton(name) for name in buttons_str]
    for b in buttons:
        buttons_layout.addWidget(b)
    buttons_container.setLayout(buttons_layout)
    if len(label_str) != 0:
        label = QLabel(f"{label_str} : ")
        layout.addWidget(label)
    layout.addWidget(buttons_container)
    container.setLayout(layout)
    return container, buttons


def image_widget(parent: QWidget = None, source_str: str = "snap-shoot.png", label_str: str = "") ->\
        Tuple[QWidget, QLabel]:
    # https://stackoverflow.com/questions/53560035/pyqt-different-image-autoscaling-modes
    # def update_evt(label):
    #     label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # def resize_evt(event, label):
    #     scaled_size = label.size()
    #     scaled_size.scale(label.size(), Qt.KeepAspectRatio)
    #     if not label.pixmap() or scaled_size != label.pixmap().size():
    #        update_evt(label)
    container    = QWidget(parent)  # контейнер с вертикальным размещением
    layout       = QVBoxLayout()
    label        = QLabel(label_str if len(label_str) != 0 else source_str.split('\\')[-1].split(".")[0])
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    label.setAlignment(Qt.AlignCenter)
    label.setMinimumSize(100, 100)
    pixmap_label = QLabel(label_str)
    pixmap       = QPixmap(source_str)
    layout.addWidget(label)
    pixmap_label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    # pixmap_label.adjustSize()
    layout.addWidget(pixmap_label)
    container.setLayout(layout)
    return container, pixmap_label

