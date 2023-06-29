# import sys
# from PyQt5.QtWidgets import (QPushButton, QDialog, QTreeWidget,
#                              QTreeWidgetItem, QVBoxLayout,
#                              QHBoxLayout, QFrame, QLabel,
#                              QApplication)
#
# from paths_container import path_container_example
#
#
# class SectionExpandButton(QPushButton):
#     """a QPushbutton that can expand or collapse its section
#     """
#     def __init__(self, item, text="", parent=None):
#         super().__init__(text, parent)
#         self.section = item
#         self.clicked.connect(self.on_clicked)
#
#     def on_clicked(self):
#         """toggle expand/collapse of section by clicking
#         """
#         if self.section.isExpanded():
#             self.section.setExpanded(False)
#         else:
#             self.section.setExpanded(True)
#
#
# class CollapsibleDialog(QDialog):
#     """a dialog to which collapsible sections can be added;
#     subclass and reimplement define_sections() to define sections and
#         add them as (title, widget) tuples to self.sections
#     """
#     def __init__(self):
#         super().__init__()
#         self.tree = QTreeWidget()
#         self.tree.setFixedSize(300, 700)
#         self.tree.setHeaderHidden(True)
#         layout = QVBoxLayout()
#         layout.addWidget(self.tree)
#         self.setLayout(layout)
#         self.tree.setIndentation(0)
#         self.setFixedSize(340, 700)
#         self.sections = []
#         self.define_sections()
#         self.add_sections()
#
#     def add_sections(self):
#         """adds a collapsible sections for every
#         (title, widget) tuple in self.sections
#         """
#         for (title, widget) in self.sections:
#             button1 = self.add_button(title)
#             section1 = self.add_widget(button1, widget)
#             button1.addChild(section1)
#
#     def define_sections(self):
#         """reimplement this to define all your sections
#         and add them as (title, widget) tuples to self.sections
#         """
#         widget = QFrame(self.tree)
#
#         path_container_example(widget)
#
#         title = "Path Container"
#         self.sections.append((title, widget))
#
#     def add_button(self, title):
#         """creates a QTreeWidgetItem containing a button
#         to expand or collapse its section
#         """
#         item = QTreeWidgetItem()
#         self.tree.addTopLevelItem(item)
#         self.tree.setItemWidget(item, 0, SectionExpandButton(item, text=title))
#         return item
#
#     def add_widget(self, button, widget):
#         """creates a QWidgetItem containing the widget,
#         as child of the button-QWidgetItem
#         """
#         section = QTreeWidgetItem(button)
#         section.setDisabled(True)
#         self.tree.setItemWidget(section, 0, widget)
#         return section
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = CollapsibleDialog()
#     window.show()
#     sys.exit(app.exec_())

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
# 1
        bar    = self.menuBar()
        self._layout = QVBoxLayout()
        self.file   = bar.addMenu("File")
        self._layout.addWidget(self.file)
        self.file.addAction("New")

        save = QAction("Save", self)
        save.setShortcut("Ctrl+S")
        self.file.addAction(save)

        edit = self.file.addMenu("Edit")
        edit.addAction("copy")
        edit.addAction("paste")

        quit = QAction(QIcon("D:/_Qt/__Qt/img/exit.png"), "Quit",self)
        quit.setShortcut('Ctrl+Q')
        quit.triggered.connect(qApp.quit)
        self.file.addAction(quit)

        self.file.triggered[QAction].connect(self.processtrigger)

# 2
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.combo = QComboBox()
        self.combo.addItems(["option1", "option2", "option3", "option4"])
        layout = QVBoxLayout(self.centralWidget)
        layout.addWidget(self.combo)

    # 1 +
    def processtrigger(self, q):
        print( q.text()+" is triggered" )

# 3
    def contextMenuEvent(self, event):
        result = self.file.exec_(self.mapToGlobal(event.pos()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.setWindowTitle("Qmenu")
    ex.resize(350,300)
    ex.show()
    sys.exit(app.exec_())

