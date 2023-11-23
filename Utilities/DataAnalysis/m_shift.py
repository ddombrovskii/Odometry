from clustering_utils import gaussian_cluster, draw_clusters, distance, gauss_core
from typing import Union, List, Tuple
import numpy as np


class MShift:
    def __init__(self):
        """
        Метод среднего сдвига.
        Этапы алгоритма:
        1. Копируем переданные данные для кластеризации "data" в "data_shifted"
        2. Для каждой точки из набора данных "data" с индексом "point_index" считаем среднее значение вокруг нее.
        3. Полученное значение на среднего сравниваем со значением под индексом "point_index" из "data_shifted"
           Если расстояние между точками меньше, чем некоторый порог "distance_threshold", то говорим, что смещать
           точку далее нет смысла и помечаем ее, как неподвижную.
           Для новой неподвижной точки пытаемся найти ближайший к ней центр кластера и добавить индекс этой точки
           к индексам точек кластера. Кластер считается ближайшим, если расстояние между точкой и центроидом
           меньше, чем "window_size".
           Если такового нет, то точка считается новым центром кластера.
        4. Пункты 2-3 повторяются до тех пор, пока все точки не будут помечены, как неподвижные.
        """
        """
        Количество кластеров, которые ожидаем обнаружить.
        """
        self._n_clusters: int = -1
        """
        Данные для кластеризации. Поле инициализируется при вызове метода fit.
        Например, если данные представляют собой координаты на плоскости,
        каждая отельная строка - это точка этой плоскости.
        """
        self._data: Union[np.ndarray, None] = None
        """
        Центры кластеров на текущем этапе кластеризации.
        """
        self._clusters_centers: Union[List[np.ndarray], None] = None
        """
        Список индексов строк из "_data", которые соответствуют определённому кластеру.
        Список списков индексов.
        """
        self._clusters_points_indices: Union[List[List[int]], None] = None
        """
        Расстояние между центроидом кластера на текущем шаге и предыдущем при котором завершается кластеризация.
        """
        self._distance_threshold: float = 1e-3
        """
        Ширина ядра функции усреднения.
        """
        self._window_size: float = 0.15

    def __repr__(self):
        return f"{{\n" \
               f"\t\"algorithm\"          : \"mean-shift\",\n" \
               f"\t\"n_samples\"          : {self.n_samples:>12},\n" \
               f"\t\"n_features\"         : {self.n_features:>12},\n" \
               f"\t\"n_clusters\"         : {self.n_clusters:>12},\n" \
               f"\t\"window_size\"        : {self.window_size:>12.3f},\n" \
               f"\t\"distance_threshold\" : {self.distance_threshold:>12.3f}\n" \
               f"}}"

    def __str__(self):
        sep = ',\n'
        nl = '\n'
        tab = '\t'

        def cluster_to_str(cluster: np.ndarray) -> str:
            return ',\n\t\t\t'.join(f'[{", ".join(f"{v:>10.4f}" for v in sample)}]'for sample in cluster)

        return f"{{\n" \
               f"\t\"algorithm\"          :     \"k-means\",\n" \
               f"\t\"n_samples\"          : {self.n_samples:>12},\n" \
               f"\t\"n_features\"         : {self.n_features:>12},\n" \
               f"\t\"n_clusters\"         : {self.n_clusters:>12},\n" \
               f"\t\"window_size\"        : {self.window_size:>12.5f},\n" \
               f"\t\"distance_threshold\" : {self.distance_threshold:>12.5f},\n" \
               f"\t\"clusters\"           : \n\t[\n{sep.join(f'{tab}{tab}[{nl}{tab}{tab}{tab}{cluster_to_str(cluster)}{nl}{tab}{tab}]'for cluster in self.clusters)}\n\t]\n" \
               f"}}"

    @property
    def window_size(self) -> float:
        """
        Просто геттер для ширины ядра функции усреднения ("_window_size").
        """
        return self._window_size

    @window_size.setter
    def window_size(self, value: float) -> None:
        """
        Сеттер для ширины ядра функции усреднения ("_window_size").
        """
        assert isinstance(value, float)
        self._window_size = max(0.0, value)

    @property
    def distance_threshold(self) -> float:
        """
        Просто геттер для "_distance_threshold".
        """
        return self._distance_threshold

    @distance_threshold.setter
    def distance_threshold(self, value: float) -> None:
        """
        Сеттер для "_distance_threshold".
        """
        assert isinstance(value, float)
        self._distance_threshold = max(0.0, value)

    @property
    def n_clusters(self) -> int:
        """
        Геттер для числа кластеров, которые обнаружили.
        """
        return 0 if self._clusters_centers is None else len(self._clusters_centers)

    @property
    def n_samples(self) -> int:
        """
        Количество записей в массиве данных. Например, количество {x, y} координат на плоскости.
        """
        return 0 if self._data is None else self._data.shape[0]

    @property
    def n_features(self) -> int:
        """
        Количество особенностей каждой записи в массив денных. Например,
        две координаты "x" и "y" в случе точек на плоскости.
        """
        return 0 if self._data is None else self._data.shape[1]

    @property
    def clusters(self) -> List[np.ndarray]:
        """
        Создаёт список из np.ndarray. Каждый такой массив - это все точки определённого кластера.
        Индексы точек соответствующих кластеру хранятся в "_clusters_points_indices"
        """
        if self._data is None:
            return []
        clusters = []
        for cluster_indices in self._clusters_points_indices:
            cluster_points = np.zeros((len(cluster_indices), self.n_features), dtype=float)
            for index, cluster_point_index in enumerate(cluster_indices):
                cluster_points[index, :] = self._data[cluster_point_index, :]
            clusters.append(cluster_points)
        return clusters

    def _clear_current_clusters(self) -> None:
        """
        Очищает центры кластеров на текущем этапе кластеризации.
        Очищает список индексов строк из "_data", которые соответствуют определённому кластеру.
        Реализует "ленивую" инициализацию полей "_clusters" и "_clusters_centers".
        """
        if self._clusters_points_indices is None:
            self._clusters_points_indices = []
            self._clusters_centers = []

        self._clusters_points_indices.clear()
        self._clusters_centers.clear()

    def _shift_cluster_point(self, point: np.ndarray) -> np.ndarray:
        """
        Функция, которая считает средне-взвешенное (если, например, используется Гауссово ядро) внутри круглого окна
        с радиусом "window_size" вокруг точки point.
        Возвращает массив равный по размеру "point".
        """
        distances = np.linalg.norm(self._data - point, axis=1)
        weights   = gauss_core(distances, self.window_size)
        w_total   = 1.0 / weights.sum()
        return (weights @ self._data) * w_total

    def _update_clusters_centers(self, sample_index, sample: np.ndarray) -> None:
        """
        Функция ищет ближайший центр кластера для точки "sample".
        Если не находит, то считает, что "sample" - новый центр кластера.
        Если находит, то добавляет к индексам точек кластера "sample_index"
        """
        if self.n_clusters == 0:
            self._clusters_centers.append(sample)
            self._clusters_points_indices.append([sample_index])
            return
        min_index, min_dist = self._get_closest_cluster_center(sample)
        if min_dist < self.window_size:
            self._clusters_points_indices[min_index].append(sample_index)
            return
        self._clusters_centers.append(sample)
        self._clusters_points_indices.append([sample_index])

    def _shift_cluster_points(self) -> None:
        """
        Выполняет итеративный сдвиг всех точек к их среднему значению.
        Т.е. для каждой точки вызывается функция _shift_cluster_point()
        Выполняется до тех пор, пока все точки не будут помечены, как неподвижные.
        """
        shifted_points = np.array(self._data)
        frozen_points_count = 0
        frozen_points = [False for _ in range(self.n_samples)]
        # or : still_shifting =[True] * self.n_samples
        while frozen_points_count != self.n_samples:
            for sample_index, sample in enumerate(shifted_points):
                if frozen_points[sample_index]:
                    continue
                shifted_sample = self._shift_cluster_point(sample)
                dist = distance(shifted_sample, sample)
                shifted_points[sample_index] = shifted_sample
                if dist > self.distance_threshold:
                    continue
                frozen_points[sample_index] = True
                frozen_points_count += 1
                self._update_clusters_centers(sample_index, shifted_sample)

    def _get_closest_cluster_center(self, sample: np.ndarray) -> Tuple[int, float]:
        """
        Определяет ближайший центр кластера для точки из переданного набора данных и расстояние до него.
        Hint: для ускорения кода используйте min с генератором.
        """
        gen = ((cluster_index, cluster_center) for cluster_index, cluster_center in enumerate(self._clusters_centers))
        min_index, min_center = min(gen, key=lambda cluster_info: distance(cluster_info[1], sample))
        return min_index, distance(sample, min_center)

    def fit(self, data: np.ndarray) -> None:
        """
        Выполняет кластеризацию данных в "data".
        1. Необходима проверка, что "data" - экземпляр класса "np.ndarray".
        2. Необходима проверка, что "data" - двумерный массив.
        Этапы работы метода:
        # 1. Проверки передаваемых аргументов
        # 2. Присваивание аргументов внутренним полям класса.
        # 3. Сдвиг точек в направлении средних значений вокруг них ("_shift_cluster_points").
        """
        assert isinstance(data, np.ndarray)
        assert data.ndim == 2
        self._data = data
        self._clear_current_clusters()
        self._shift_cluster_points()

    def show(self) -> None:
        draw_clusters(self.clusters, cluster_centers=self._clusters_centers, title="Mean shift clustering")


def separated_clusters():
    m_shift = MShift()
    clusters_data = np.vstack((gaussian_cluster(cx=0.5, n_points=1024),
                               gaussian_cluster(cx=1.0, n_points=1024),
                               gaussian_cluster(cx=1.5, n_points=1024),
                               gaussian_cluster(cx=2.0, n_points=1024),
                               gaussian_cluster(cx=2.5, n_points=1024)))
    m_shift.fit(clusters_data)
    print(repr(m_shift))
    with open('clusters.json', 'wt') as output_clusters:
        print(m_shift, file=output_clusters)
    m_shift.show()


def merged_clusters():
    m_shift = MShift()
    m_shift.fit(gaussian_cluster(n_points=1024))
    print(repr(m_shift))
    m_shift.show()


if __name__ == "__main__":
    merged_clusters()
    separated_clusters()
