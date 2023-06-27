from typing import List


class CircBuffer:
    """
    Кольцевой буфер
    """
    def _index(self, index: int) -> int:
        return (index + self._indent) % self.capacity

    def __init__(self, cap: int):
        self._indent: int = 0
        self._n_items: int = 0
        self._values: List[float] = [0.0 for _ in range(cap)]

    def __getitem__(self, index: int):
        if index >= self.n_items or index < 0:
            raise IndexError(f"CircBuffer :: trying to access index: {index}, while cap is {self.capacity}")
        return self._values[self._index(index)]

    def __setitem__(self, index: int, value):
        if index >= self.n_items or index < 0:
            raise IndexError(f"CircBuffer :: trying to access index: {index}, while cap is {self.capacity}")
        self._values[self._index(index)] = value

    def __str__(self):
        return f"[{', '.join(str(item) for item in self)}]"

    @property
    def n_items(self) -> int:
        return self._n_items

    @property
    def capacity(self) -> int:
        return len(self._values)

    @property
    def sorted(self) -> list:
        return sorted(self._values)

    def append(self, value) -> None:
        """
        Добавляет новый элемент в буфер
        """
        self._values[self._index(self.n_items)] = value
        if self.n_items != self.capacity:
            self._n_items += 1
        else:
            self._indent += 1
            self._indent %= self.capacity

    def peek(self) -> float:
        """
        Возвращает последний добавленный элемент
        """
        if self.n_items == 0:
            raise IndexError(f"CircBuffer :: pop :: items amount is {self.n_items}")
        value = self._values[self._index(self.n_items - 1)]
        return value

    def pop(self) -> float:
        """
        Возвращает последний добавленный элемент и удаляет его же
        """
        value = self.peek()
        self._n_items -= 1
        return value

    def clear(self) -> None:
        """
        Очищает буфер
        """
        self._indent = 0
        self._n_items = 0
