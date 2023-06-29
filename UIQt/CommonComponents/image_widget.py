import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QLabel, QApplication


class ImageWidget(QLabel):
    def __init__(self, source_str: str):
        super(ImageWidget, self).__init__()
        self.pixmap_width: int = 1
        self.pixmapHeight: int = 1
        self._source_str = source_str
        self._pxmap = QPixmap(self._source_str)
        self.setPixmap(self._pxmap)
        self.setScaledContents(True)

    @property
    def pxmap(self) -> str:
        return self._source_str

    @pxmap.setter
    def pxmap(self, pm: str) -> None:
        pixmap = QPixmap(pm)
        self.setPixmap(pixmap)

    def setPixmap(self, pm: QPixmap) -> None:
        self.pixmap_width = pm.width()
        self.pixmapHeight = pm.height()

        self.updateMargins()
        super(ImageWidget, self).setPixmap(pm)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.updateMargins()
        super(ImageWidget, self).resizeEvent(event)

    def updateMargins(self):
        if self.pixmap() is None:
            return
        pixmapWidth = self.pixmap().width()
        pixmapHeight = self.pixmap().height()
        if pixmapWidth <= 0 or pixmapHeight <= 0:
            return
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        if w * pixmapHeight > h * pixmapWidth:
            m = int((w - (pixmapWidth * h / pixmapHeight)) / 2)
            self.setContentsMargins(m, 0, m, 0)
        else:
            m = int((h - (pixmapHeight * w / pixmapWidth)) / 2)
            self.setContentsMargins(0, m, 0, m)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageWidget("snap-shoot.png")
    window.show()
    sys.exit(app.exec_())