from PyQt5 import uic  # если пайчарм подсвечивает ошибку, то это ОК, просто баг пайчарма
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QStyle, QFileDialog, QFrame, QTextEdit
from PyQt5.QtGui import QPixmap


# UNUSED
class ReferenceViewWidget(QWidget):
    def __init__(self, number: int):
        super(ReferenceViewWidget, self).__init__()
        uic.loadUi("./UI/ReferenceViewWidget.ui", self)
        self.number = number
        deleteIconPixmap = self.style().standardIcon(getattr(QStyle, "SP_DockWidgetCloseButton"))

        self.setStyleSheet('background-color: #D3D3D3;')

        self.shadeIconPixmap = self.style().standardIcon(getattr(QStyle, "SP_TitleBarShadeButton"))
        self.unshadeIconPixmap = self.style().standardIcon(getattr(QStyle, "SP_TitleBarUnshadeButton"))

        self.deleteBtn: QPushButton = self.findChild(QPushButton, "deleteBtn")
        self.deleteBtn.setIcon(deleteIconPixmap)
        self.deleteBtn.clicked.connect(self.delete_clicked)

        self.refViewLabel: QLabel = self.findChild(QLabel, "refViewLabel")
        ref_view_image, _ = QFileDialog.getOpenFileName(None, 'Выберите изображение опорного ракурса', './', "Image (*.png *.jpg *jpeg)")
        self.refViewPixmap = QPixmap(ref_view_image)
        self.refViewLabel.setPixmap(self.refViewPixmap.scaled(222, 100))

        self.matrixesFrame: QFrame = self.findChild(QFrame, "matrixesFrame")

        self.collapseBtn: QPushButton = self.findChild(QPushButton, "collapseBtn")
        self.collapseBtn.clicked.connect(self.collapse)

        self.transformMatrixTextEdit: QTextEdit = self.findChild(QTextEdit, "transformMatrixTextEdit")
        self.projectionMatrixTextEdit: QTextEdit = self.findChild(QTextEdit, "projectionMatrixTextEdit")

        self.transformMatrixTextEdit.setText("11 12 13 14\n21 22 23 24\n31 32 33 34\n41 42 43 44")
        self.projectionMatrixTextEdit.setText("11 12 13 14\n21 22 23 24\n31 32 33 34\n41 42 43 44")

        self.currentCollapseState = False
        self.collapse()


    def collapse(self):
        if self.currentCollapseState:
            self.transformMatrixTextEdit.show()
            self.projectionMatrixTextEdit.show()
            self.collapseBtn.setIcon(self.shadeIconPixmap)
        else:
            self.transformMatrixTextEdit.hide()
            self.projectionMatrixTextEdit.hide()
            self.collapseBtn.setIcon(self.unshadeIconPixmap)
        self.currentCollapseState = not self.currentCollapseState

    def delete_clicked(self):
        self.deleteLater()
