from PyQt5.QtWidgets import QLabel, QApplication, QWidget
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtGui import QPixmap
import sys


class ImageWidget(QLabel):
    def __init__(self, source_str: str = None, parent: QWidget = None):
        super(ImageWidget, self).__init__(parent)
        self._pixmap_src = source_str
        self._load_pix_map()
        self.setScaledContents(True)

    def _load_pix_map(self):
        try:
            pm = QPixmap(self._pixmap_src)
        except FileNotFoundError as ex:
            try:
                self._pixmap_src = "snap-shoot.png"
                pm = QPixmap(self._pixmap_src)
            except FileNotFoundError as ex:
                pm = None
        if pm is None:
            self._pixmap_src = "none image"
            return
        self.setPixmap(pm)

    @property
    def pixmap_src(self) -> str:
        return self._pixmap_src

    @pixmap_src.setter
    def pixmap_src(self, pm: str) -> None:
        self._pixmap_src = pm
        self._load_pix_map()

    def setPixmap(self, pm: QPixmap) -> None:
        self.update_margins()
        super(ImageWidget, self).setPixmap(pm)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.update_margins()
        super(ImageWidget, self).resizeEvent(event)

    def update_margins(self):
        if self.pixmap() is None:
            return
        pixmap_width = self.pixmap().width()
        pixmap_height = self.pixmap().height()
        if pixmap_width <= 0 or pixmap_height <= 0:
            return
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return
        if w * pixmap_height > h * pixmap_width:
            m = int((w - (pixmap_width * h / pixmap_height)) / 2)
            self.setContentsMargins(m, 0, m, 0)
        else:
            m = int((h - (pixmap_height * w / pixmap_width)) / 2)
            self.setContentsMargins(0, m, 0, m)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageWidget("snap-shoot.png")
    window.show()
    sys.exit(app.exec_())
