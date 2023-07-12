import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from image_widget import ImageWidget

class CollapsableWidget(QWidget):
    def __init__(self, inner: QWidget = None):
        super(CollapsableWidget, self).__init__()
        self._btn = QPushButton()
        self._btn.clicked.connect(self.collapse)
        self._layout: QVBoxLayout | None = QVBoxLayout()
        self._inner: QWidget | None = inner
        self._layout.addWidget(self._btn)
        self._layout.addWidget(self._inner)
        self.setLayout(self._layout)
        self._inner.show()

    def collapse(self):
        if self._inner.isHidden():
            self._inner.show()
        else:
            self._inner.hide()

    @property
    def btn(self) -> QPushButton:
        return self._btn

    @btn.setter
    def btn(self, btn_str: str) -> None:
        self._btn.setText(btn_str)

    @property
    def inner(self) -> QWidget:
        return self._inner

    @inner.setter
    def inner(self, inner: QWidget) -> None:
        self._inner = inner


if __name__ == "__main__":
    app = QApplication(sys.argv)

    label = ImageWidget()
    inner = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(label)
    inner.setLayout(layout)
    win = CollapsableWidget(None, inner)

    win.show()
    sys.exit(app.exec_())