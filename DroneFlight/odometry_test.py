from Utilities.Geometry import Quaternion
from Utilities.CV import FlightOdometer
from Utilities.CV import ImageMatcher
from matplotlib import pyplot as plt
from Utilities import io_utils
import numpy as np
import os.path
import cv2


def image_index(img) -> int:
    try:
        return int((img.split('_')[-1]).split('.')[0])
    except ValueError as err:
        error_str = f"file name without \"_\" separator, file name: {img}"
    try:
        return int(img.split('\\')[-1][5:].split('.')[0])
    except ValueError as err:
       error_str = f"file name starts without key word \"image\", file name: {img}"
    raise ValueError(error_str)


def get_sorted_images_paths(directory: str):
    images = [f"{os.path.join(directory, src)}" for src in os.listdir(directory) if src.endswith('png') or src.endswith('JPG')]
    return sorted(images, key=image_index)


def drone_odometry(directory: str, log_file_path: str = None):
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
    if log_file_path is None:
        for image_src in images_sources:
            # Симуляция одометрии
            image = io_utils.read_image(image_src, cv2.IMREAD_GRAYSCALE)
            flight_odometer.compute(image, rot_q, 10)
            positions_x.append(flight_odometer.position.x)
            positions_y.append(flight_odometer.position.y)
    else:
        # как включить логирование
        with open(log_file_path, 'wt', encoding='utf-8') as log_file:
            flight_odometer.enable_logging(log_file)
            for image_src in images_sources:
                # Симуляция одометрии
                image = io_utils.read_image(image_src, cv2.IMREAD_GRAYSCALE)
                flight_odometer.compute(image, rot_q, 10)
                positions_x.append(flight_odometer.position.x)
                positions_y.append(flight_odometer.position.y)
            flight_odometer.disable_logging()

    # Вывод результатов одометрии
    fig, axs = plt.subplots(1)
    axs.plot(positions_x, positions_y, 'r')
    axs.set_aspect('equal', 'box')
    axs.set_title('odometry')
    axs.set_xlabel("x")
    axs.set_ylabel("y")
    axs.grid(True)
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
    axs.set_title('homography')
    axs.set_xlabel("x")
    axs.set_ylabel("y")
    axs.grid(True)
    plt.show()


if __name__ == "__main__":
    # images_directory = 'path_track'
    images_directory = "Utilities/sim_imgs"
    drone_odometry(images_directory, 'odom_log.json')
    image_matching_odometry(images_directory)
