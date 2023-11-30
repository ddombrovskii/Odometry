from Utilities import io_utils
from clustering_utils import gaussian_cluster, draw_clusters, distance
from typing import Union, List
import numpy as np
import random


class KMeans:
    """
    Метод К-средних соседей.
    Этапы алгоритма:
    1. Выбирается число кластеров k.
    2. Из исходного множества данных случайным образом выбираются k наблюдений,
       которые будут служить начальными центрами кластеров.
    3. Для каждого наблюдения исходного множества определяется ближайший к нему центр кластера
       (расстояния измеряются в метрике Евклида). При этом записи,
        «притянутые» определенным центром, образуют начальные кластеры
    4. Вычисляются центроиды — центры тяжести кластеров. Каждый центроид — это вектор, элементы которого
       представляют собой средние значения соответствующих признаков, вычисленные по всем записям кластера.
    5. Центр кластера смещается в его центроид, после чего центроид становится центром нового кластера.
    6. 3-й и 4-й шаги итеративно повторяются. Очевидно, что на каждой итерации происходит изменение границ
       кластеров и смещение их центров. В результате минимизируется расстояние между элементами внутри
       кластеров и увеличиваются между-кластерные расстояния.
    Примечание: Ниже описана функциональная структура, которую использовал я. Вы можете модифицировать или вовсе
                отойти в сторону от неё. Главное, что требуется это реализация пунктов 1-6.
    """
    def __init__(self, n_clusters: int):
        """
        Метод к-средних соседей.
        """
        """
        Количество кластеров, которые ожидаем обнаружить.
        """
        self._n_clusters: int = n_clusters
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
        self._distance_threshold: float = 0.1

    def __repr__(self):
        return f"{{\n" \
               f"\t\"algorithm\"          :     \"k-means\",\n" \
               f"\t\"n_samples\"          : {self.n_samples:>12},\n" \
               f"\t\"n_features\"         : {self.n_features:>12},\n" \
               f"\t\"n_clusters\"         : {self.n_clusters:>12},\n" \
               f"\t\"distance_threshold\" : {self.distance_threshold:>12.5f}\n" \
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
               f"\t\"distance_threshold\" : {self.distance_threshold:>12.5f},\n" \
               f"\t\"clusters\"           : \n\t[\n{sep.join(f'{tab}{tab}[{nl}{tab}{tab}{tab}{cluster_to_str(cluster)}{nl}{tab}{tab}]'for cluster in self.clusters)}\n\t]\n" \
               f"}}"

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
        Геттер для числа кластеров, которые ожидаем обнаружить.
        """
        return self._n_clusters

    @n_clusters.setter
    def n_clusters(self, value: int) -> None:
        """
        Сеттер для числа кластеров, которые ожидаем обнаружить.
        """
        assert isinstance(value, int)
        self._n_clusters = max(1, value)

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
        return [] if self._data is None else [self._data[c_idxs] for c_idxs in self._clusters_points_indices]

    def _clear_current_clusters(self) -> None:
        """
        Очищает центры кластеров на текущем этапе кластеризации.
        Очищает список индексов строк из "_data", которые соответствуют определённому кластеру.
        Реализует "ленивую" инициализацию полей "_clusters_points_indices" и "_clusters_centers".
        """
        if self._clusters_points_indices is None:
            self._clusters_points_indices = []
            self._clusters_centers = []

        self._clusters_points_indices.clear()
        self._clusters_centers.clear()

    def _create_start_clusters_centers(self) -> None:
        """
        Случайным образом выбирает n_clusters точек из переданных данных в качестве начальных центроидов кластеров.
        Точки нужно выбрать таким образом, что бы они не повторялись
        """
        self._clear_current_clusters()
        clusters_ids = set()  # Проверка, что мы не воткнём две одинаковые точки, как центр кластера.
        while len(self._clusters_points_indices) != self.n_clusters:
            cluster_center_index = random.randint(0, self.n_samples - 1)
            if cluster_center_index in clusters_ids:
                continue
            clusters_ids.update({cluster_center_index})
            self._clusters_centers.append(self._data[cluster_center_index, :])
            self._clusters_points_indices.append([])

    def _get_closest_cluster_center(self, sample: np.ndarray) -> int:
        """
        Определяет ближайший центр кластера для точки из переданного набора данных.
        """
        gen = ((cluster_index, cluster_center) for cluster_index, cluster_center in enumerate(self._clusters_centers))
        min_index, min_center = min(gen, key=lambda cluster_info: distance(cluster_info[1], sample))
        return min_index

    def _clusterize_step(self) -> List[np.ndarray]:
        """
        Определяет списки индексов точек из "_data", наиболее близких для того или иного кластера.
        На основе этих список вычисляются новые центры кластеров.
        """
        for cluster in self._clusters_points_indices:
            cluster.clear()
        for sample_index, sample in enumerate(self._data):
            cluster_index = self._get_closest_cluster_center(sample)
            self._clusters_points_indices[cluster_index].append(sample_index)
        centroids = []
        for cluster_id, cluster_sample_indices in enumerate(self._clusters_points_indices):
            if len(cluster_sample_indices) == 0:
                continue
            centroids.append(np.mean(self._data[cluster_sample_indices, :], axis=0))
        return centroids

    def fit(self, data: np.ndarray, target_clusters: int = None) -> None:
        """
        Выполняет кластеризацию данных в "data".
        1. Необходима проверка, что "data" - экземпляр класса "np.ndarray".
        2. Необходима проверка, что "data" - двумерный массив.
        Этапы работы метода:
        1. Проверки передаваемых аргументов
        2. Присваивание аргументов внутренним полям класса.
        3. Построение начальных центроидов кластеров "_create_start_clusters_centers"
        4. Цикл уточнения положения центроидов. Выполнять пока расстояние между текущим центроидом
           кластера и предыдущим больше, чем "distance_threshold"
        """
        assert isinstance(data, np.ndarray)
        assert data.ndim == 2
        self.n_clusters = self.n_clusters if target_clusters is None else target_clusters
        self._data = data
        self._create_start_clusters_centers()
        prev_centroids = self._clusters_centers
        curr_centroids = self._clusterize_step()
        while not all(distance(left, right) < self.distance_threshold for left, right in
                      zip(prev_centroids, curr_centroids)):
            curr_centroids = self._clusterize_step()
            prev_centroids, self._clusters_centers = self._clusters_centers, curr_centroids

    def show(self):
        """
        Выводит результат кластеризации в графическом виде
        """
        draw_clusters(self.clusters, cluster_centers=self._clusters_centers, title="K-means clustering" )


def separated_clusters():
    """
    Пример с пятью разрозненными распределениями точек на плоскости.
    """
    k_means = KMeans(5)
    clusters_data = np.vstack((gaussian_cluster(cx=0.5, n_points=512),
                               gaussian_cluster(cx=1.0, n_points=512),
                               gaussian_cluster(cx=1.5, n_points=512),
                               gaussian_cluster(cx=2.0, n_points=512),
                               gaussian_cluster(cx=2.5, n_points=512)))
    k_means.fit(clusters_data)
    print(repr(k_means))
    k_means.show()


def merged_clusters():
    """
    Пример с кластеризацией пятна.
    """
    k_means = KMeans(5)
    k_means.fit(gaussian_cluster(n_points=128))
    print(repr(k_means))
    with open('clusters.json', 'wt') as output_clusters:
        print(k_means, file=output_clusters)
    k_means.show()


if __name__ == "__main__":
    """
    Сюрприз-сюрприз! Вызов функций "merged_clusters" и "separated_clusters".
    """
    merged_clusters()
    separated_clusters()
