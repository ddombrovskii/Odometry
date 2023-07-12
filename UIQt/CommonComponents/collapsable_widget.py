import sys
from PyQt5.QtCore import QObject, QPoint, QPointF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (QPushButton, QDialog, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout,
                             QHBoxLayout, QFrame, QLabel,
                             QApplication, QWidget)
from image_widget import ImageWidget


"""
#############################
#           ARROW           #
#############################
"""


class Arrow(QFrame):
    def __init__(self, parent=None, collapsed=False):
        super().__init__(parent=parent)
        self.setMaximumSize(24, 24)
        # horizontal == 0
        self._arrow_horizontal = (QPointF(7.0, 8.0), QPointF(17.0, 8.0), QPointF(12.0, 13.0))
        # vertical == 1
        self._arrow_vertical = (QPointF(8.0, 7.0), QPointF(13.0, 12.0), QPointF(8.0, 17.0))
        # arrow
        self._arrow = None
        self.set_arrow(int(collapsed))

    def set_arrow(self, arrow_dir):
        if arrow_dir:
            self._arrow = self._arrow_vertical
        else:
            self._arrow = self._arrow_horizontal

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QColor(192, 192, 192))
        painter.setPen(QColor(64, 64, 64))
        painter.drawPolygon(*self._arrow)
        painter.end()

"""
############################
#           TITLE          #
############################
"""


class TitleFrame(QFrame):
    def __init__(self, parent=None, title="", collapsed=False):
        super().__init__(parent=parent)
        self.setMinimumHeight(24)
        self.move(QPoint(24, 0))
        self.setStyleSheet("border:1px solid rgb(41, 41, 41); ")

        self._h_layout = QHBoxLayout(self)
        self._h_layout.setContentsMargins(0, 0, 0, 0)
        self._h_layout.setSpacing(0)

        self._arrow = None
        self._title = None

        self._h_layout.addWidget(self.init_arrow(collapsed))
        self._h_layout.addWidget(self.init_title(title))

    def init_arrow(self, collapsed):
        self._arrow = Arrow(parent=self, collapsed=collapsed)
        self._arrow.setStyleSheet("border:0px")

        return self._arrow

    def init_title(self, title=None):
        self._title = QLabel(title)
        self._title.setMinimumHeight(24)
        self._title.move(QPoint(24, 0))
        self._title.setStyleSheet("border:0px")
        return self._title

    def mousePressEvent(self, event):
        # TODO FIX
        self.emit(SIGNAL('clicked()'))
        return super(TitleFrame, self).mousePressEvent(event)

    @property
    def title(self) -> QLabel:
        return self._title

    @property
    def arrow(self) -> Arrow:
        return self._arrow


class FrameLayout(QWidget):
    def __init__(self, parent=None, title=None):

        super().__init__(parent=parent)
        self._is_collapsed = True
        self._title_frame = None
        self._content, self._content_layout = (None, None)

        self._main_v_layout = QVBoxLayout(self)
        self._main_v_layout.addWidget(self.init_frame_title(title, self._is_collapsed))
        self._main_v_layout.addWidget(self.init_content(self._is_collapsed))

        self.init_collapsable()

    def init_frame_title(self, title: str, collapsed: bool):
        self._title_frame = TitleFrame(parent=self, title=title, collapsed=collapsed)

        return self._title_frame

    def init_content(self, collapsed: bool):
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content.setLayout(self._content_layout)
        self._content.setVisible(not collapsed)

        return self._content

    def add_widget(self, widget):
        self._content_layout.addWidget(widget)

    def init_collapsable(self):
        # TODO FIX
        QObject.connect(self._title_frame, SIGNAL('clicked()'), self.toggle_collapsed)

    def toggle_collapsed(self):
        self._content.setVisible(self._is_collapsed)
        self._is_collapsed = not self._is_collapsed
        self._title_frame.arrow.set_arrow(int(self._is_collapsed))


if __name__ == "__main__":
    # TODO FIX
    app = QApplication(sys.argv)
    window = CollapsibleDialog()
    window.show()
    sys.exit(app.exec_())
