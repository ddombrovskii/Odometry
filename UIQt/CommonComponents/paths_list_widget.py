from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from typing import Dict


class PathsListWidget(QWidget):
    """
    Класс контейнер для элементов. Позволяет добавить элементы или удалить их.
    """
    def __init__(self, parent: QWidget = None, width: int = 300, height: int = 600, window_name: str = "MainWindow"):
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert isinstance(window_name, str)
        super(PathsListWidget, self).__init__(parent)
        self._widgets = {}
        self._list_widget: QListWidget | None = QListWidget()
        self._layout:      QVBoxLayout | None = QVBoxLayout()
        self._layout.addWidget(self._list_widget)
        self.setLayout(self._layout)

    @property
    def list_elements_widgets(self) -> Dict[int, QWidget]:
        return self._widgets

    @property
    def container(self) -> QWidget:
        """
        Контейнер с элементами
        """
        return self

    @property
    def list_widget(self) -> QListWidget:
        """
        Контейнер с элементами
        """
        return self._list_widget

    def register_element(self, element: QWidget) -> int:
        """
        Привязвыет элементы интерфейса к родителю
        """
        unique_id = id(element)
        if id(element) in self._widgets:
            return -1
        self._widgets.update({unique_id: element})
        list_item_widget  = QListWidgetItem(self._list_widget)
        list_item_widget.setSizeHint(element.sizeHint())
        self._list_widget.addItem(list_item_widget)
        self._list_widget.setItemWidget(list_item_widget, element)
        return unique_id

    def unregister_element(self, element: QWidget | int) -> bool:
        # TODO проверить адекватность работы
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
        item = self._widgets[unique_id]
        item.deleteLater()
        self._list_widget.removeItemWidget(item)
        del self._widgets[unique_id]
        return True
