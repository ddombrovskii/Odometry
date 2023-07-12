class RunningAverage:
    def __init__(self, bucket_size: int = 8):
        self._values     = []
        self._values_sum = 0.0
        self._capacity   = min(max(bucket_size, 2), 128)

    def reset(self):
        self._values     = []
        self._values_sum = 0.0

    @property
    def window_size(self) -> int:
        return self._capacity

    @window_size.setter
    def window_size(self, value: int) -> None:
        assert isinstance(value, int)
        self._capacity = min(max(value, 2), 128)

    def __call__(self, x) -> float:
        return self.update(x)

    def update(self, x) -> float:
        self._values.append(x)
        self._values_sum += x
        if len(self._values) == self._capacity:
            self._values_sum -= self._values[0]
            del self._values[0]
        return self._values_sum / len(self._values)