from Utilities.flight_odometer import FlightOdometer
from Utilities import io_utils
from Utilities.Geometry import Quaternion
from matplotlib import pyplot as plt
import numpy as np
import os.path
import cv2

from Utilities.image_matcher import ImageMatcher


def image_index(img) -> int:
    return int((img.split('_')[-1]).split('.')[0])


def get_sorted_images_paths(directory: str):
    images = [f"{os.path.join(directory, src)}" for src in os.listdir(directory) if src.endswith('png') or src.endswith('JPG')]
    return sorted(images, key=image_index)


def drone_odometry(directory: str):
    # Чтение изображений
    images_sources = get_sorted_images_paths(directory)
    # Вывод путей к изображениям
    [print(src) for src in images_sources]
    # Инициализация нового одометра
    flight_odometer = FlightOdometer()
    # Кватернион поворота. Нам интересны в первую очередь углы x и y
    rot_q = Quaternion.from_euler_angles(0.0, 0.0, 0.0, False)
    positions_x = []
    positions_y = []
    for image_src in images_sources:
        # Симуляция одометрии
        image = io_utils.read_image(image_src, cv2.IMREAD_GRAYSCALE)
        flight_odometer.compute(image, rot_q, 10)
        positions_x.append(flight_odometer.position.x)
        positions_y.append(flight_odometer.position.y)
    # Вывод результатов одометрии
    fig, axs = plt.subplots(1)
    axs.plot(positions_x, positions_y, 'r')
    axs.set_aspect('equal', 'box')
    plt.show()


def image_matching_odometry(directory: str):
    # Чтение изображений
    images_sources = get_sorted_images_paths(directory)
    # Вывод путей к изображениям
    [print(src) for src in images_sources]
    # Инициализация алгоритма совмещения изображений
    img_matcher = ImageMatcher()
    # расчёт цепи последовательных трансформаций
    transforms = [img_matcher.homography_matrix for img_1, img_2 in zip(images_sources[:-1], images_sources[1:])
                  if img_matcher.match_images_from_file(img_1, img_2)]
    curr_t = transforms[0]
    positions_x = []
    positions_y = []
    # восстановление положений по матрицам трансформаций
    for next_t in transforms[1:]:
        curr_t *= next_t
        positions_x.append(curr_t.m02)
        positions_y.append(curr_t.m12)
    positions_x = np.array(positions_x)
    positions_y = np.array(positions_y)
    # Вывод результатов одометрии
    fig, axs = plt.subplots(1)
    axs.plot(positions_x, positions_y, 'r')
    axs.set_aspect('equal', 'box')
    plt.show()


if __name__ == "__main__":
    images_directory = 'path_track'
    drone_odometry(images_directory)
    image_matching_odometry(images_directory)
