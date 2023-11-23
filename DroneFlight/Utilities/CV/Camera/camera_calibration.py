from collections import namedtuple
from typing import List, Union
import numpy as np
import json
import cv2
import os

IMAGE_TYPES = {'bmp', 'png', 'jpg', 'tga'}


def get_images_in_dir(directory: str) -> List[str]:
    return [f"{directory}\\{file}" for file in os.listdir(directory) if any(file.endswith(v) for v in IMAGE_TYPES)]


class CameraCalibrationInfo(namedtuple('CameraCalibrationInfo', 'camera_matrix, distortion_coefficients,'
                                                                ' translation_vectors, rotation_vectors')):
    """
    Результаты калибровки камеры.
    """
    __slots__ = ()

    def __new__(cls, cm: np.ndarray, dc: np.ndarray,
                tv: Union[np.ndarray, None] = None,
                rv: Union[np.ndarray, None] = None):
        """
        Параметры калибровки камеры.
        :param cm: матрица камеры.
        :param dc: массив дисторсионных коэффициентов.
        :param tv: массив векторов смещений.
        :param rv: массив векторов поворотов.
        """
        if cm.shape != (3, 3):
            raise ValueError("CameraCalibrationInfo: camera_matrix.size != (3,3)")
        tv = np.array([]) if tv is None else np.array([[vi for vi in v.flat] for v in tv])
        rv = np.array([]) if rv is None else np.array([[vi for vi in v.flat] for v in rv])
        return super().__new__(cls, cm, dc, tv, rv)

    def __str__(self):
        _fmt = '>20.5f'

        def print_(vectors: np.ndarray):
            return ',\n\t\t'.join(f"{{ "
                                  f"\"x\": {v[0]:{_fmt}}, "
                                  f"\"y\": {v[1]:{_fmt}}, "
                                  f"\"z\": {v[2]:{_fmt}}}}" for v in vectors)
        return "{\n\t\"camera_matrix\": \n\t{\n" \
               f"\t\t\"m00\": {self.camera_matrix[0][0]:{_fmt}}, \"m01\": {self.camera_matrix[0][1]:{_fmt}}, \"m02\":"\
               f" {self.camera_matrix[0][2]:{_fmt}},\n"\
               f"\t\t\"m10\": {self.camera_matrix[1][0]:{_fmt}}, \"m11\": {self.camera_matrix[1][1]:{_fmt}}, \"m12\":"\
               f" {self.camera_matrix[1][2]:{_fmt}},\n"\
               f"\t\t\"m20\": {self.camera_matrix[2][0]:{_fmt}}, \"m21\": {self.camera_matrix[2][1]:{_fmt}}, \"m22\":"\
               f" {self.camera_matrix[2][2]:{_fmt}}\n\t}},\n" \
               f"\t\"distortion\": " \
               f"\n\t[\n\t\t{', '.join(f'{value:{_fmt}}' for value in self.distortion_coefficients.flat)}\n\t],\n"\
               f"\t\"translation_vectors\": \n\t[\n\t\t{(print_(self.translation_vectors))}\n\t],\n"\
               f"\t\"rotation_vectors\": \n\t[\n\t\t{(print_(self.rotation_vectors))}\n\t]\n}}"


def load_camera_calib_info(file_path: str) -> Union[CameraCalibrationInfo, None]:
    """
    :param file_path: путь к файлу с результатами калибровки.
    :return:
    """
    assert isinstance(file_path, str)
    if not os.path.exists(file_path):
        return None

    with open(file_path, "rt", encoding='utf-8') as input_file:
        json_file = json.load(input_file)
        if json_file is None:
            return None
        cm = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        dc = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        tv = []
        rv = []
        if "camera_matrix" in json_file:
            node = json_file["camera_matrix"]
            for i in range(9):
                row, col = divmod(i, 3)
                try:
                    cm[row][col] = float(node[f"m{row}{col}"])
                except ValueError or KeyError as _ex:
                    val = node[f"m{row}{col}"]
                    print(f"camera_matrix read error: m{row}{col} = {val}]")

        if "translation_vectors" in json_file:
            nodes = json_file["translation_vectors"]
            for node in nodes:
                try:
                    tv.append([float(node["x"]), float(node["y"]), float(node["z"])])
                except ValueError or KeyError as _ex:
                    print(f"translation_vectors read error: {node['x']}, {node['y']}, {node['z']}]")

        if "rotation_vectors" in json_file:
            nodes = json_file["rotation_vectors"]
            for node in nodes:
                try:
                    rv.append([float(node["x"]), float(node["y"]), float(node["z"])])
                except ValueError or KeyError as _ex:
                    print(f"rotation_vectors read error: {node['x']}, {node['y']}, {node['z']}]")

        if "distortion" in json_file:
            node = json_file["distortion"]
            for index, val in enumerate(node):
                try:
                    dc[index] = float(val)
                except ValueError or KeyError as _ex:
                    print(f"distortion read error at index: {index}, with val: {val}]")
    return CameraCalibrationInfo(cm, dc, np.array(tv), np.array(rv))


class CameraCalibrationArgs(namedtuple('CameraCalibrationArgs',
                                       'criteria, obj_points, image_points, '
                                       'ches_board_size, obj_points_array, recalibrate')):
    """
    Настройки алгоритма калибровки камеры.
    """
    __slots__ = ()

    def __new__(cls, criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                ches_board_size=(6, 6), recalibrate=False):
        _obj_p: np.ndarray = np.zeros((ches_board_size[0] * ches_board_size[1], 3), dtype=np.float32)
        _obj_p[:, :2] = np.mgrid[0:ches_board_size[0], 0:ches_board_size[1]].T.reshape(-1, 2)
        return super().__new__(cls, criteria, [], [], ches_board_size, _obj_p, recalibrate)

    def __str__(self):
        sep  = ' ,'
        return f"{{\n" \
               f"\t\"criteria\":        [{sep.join(f'{v:>.3f}' for v in self.criteria)}],\n" \
               f"\t\"ches_board_size\": [{self.ches_board_size[0]:>5}, {self.ches_board_size[1]:>5}],\n" \
               f"\t\"recalibrate\":     \"{'true' if self.recalibrate else 'false'}\"\n" \
               f"}}"


def load_camera_calib_args(file_path: str) -> Union[CameraCalibrationArgs, None]:
    """
    :param file_path: путь к файлу с настройками для калибровки.
    :return:
    """
    assert isinstance(file_path, str)
    if not os.path.exists(file_path):
        return None

    with open(file_path, "rt", encoding='utf-8') as input_file:
        json_file = json.load(input_file)
        if json_file is None:
            return None
        criteria = None
        recalibrate = None
        board_size = None
        if "criteria" in json_file:
            node = json_file["criteria"]
            try:
                criteria = tuple(map(float, node))
            except ValueError or KeyError as _ex:
                print(f"criteria read error: [{', '.join(str(v) for v in node)}]")

        if "ches_board_size" in json_file:
            node = json_file["criteria"]
            try:
                board_size = tuple(map(int, node))
            except ValueError or KeyError as _ex:
                print(f"board size read error: [{', '.join(str(v) for v in node)}]")

        if "recalibrate" in json_file:
            recalibrate = True if json_file["recalibrate"] == 'true' else False

        if not all(v is not None for v in (criteria, recalibrate, board_size)):
            return None

    return CameraCalibrationArgs(criteria, board_size, recalibrate)


def compute_camera_calibration_data(images_directory: str, args: CameraCalibrationArgs, n_images: int = -1) ->\
        Union[None, CameraCalibrationInfo]:
    """
    :param images_directory: путь к директории с кадрами для калибровки.
    :param args: настройки для калибровки.
    :param n_images: количество изображений, для которых рассчитывается калибровка.
    :return:
    """
    images_src_s = get_images_in_dir(images_directory)
    calibration_params = CameraCalibrationArgs() if args is None else args
    image_w, image_h = -1, -1

    if n_images < 0:
        n_images = len(images_src_s)

    images_src_s = images_src_s[0:min(len(images_src_s), n_images)]

    for img in images_src_s:
        print(f"processing image: \"{img}\"")
        # чтение и перевод кадра в серый цвет
        image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        if image_w == -1 and image_h == -1:
            image_w, image_h = image.shape[1], image.shape[0]
        elif image_w != image.shape[1] or image_h != image.shape[0]:
            raise ValueError("Размер калибровочных изображений непостоянен")
        else:
            image_w, image_h = image.shape[1], image.shape[0]
        # поиск углов шахматной доски
        ret, corners = cv2.findChessboardCorners(image, calibration_params.ches_board_size, None)
        if not ret:
            print(f"no corners found at image: \"{img}\"")
            continue
        calibration_params.obj_points.append(calibration_params.obj_points_array)
        calibration_params.image_points.append(corners)
        # corners_2 = cv2.cornerSubPix(image, corners, (11, 11), (-1, -1), calibration_params.criteria)
        # curr_frame = cv2.drawChessboardCorners(image, calibration_params.ches_board_size, corners_2, ret)
        # cv2.imshow("calibration", curr_frame)
        # time.sleep(1.0)

    calib_results: Union[None, CameraCalibrationInfo] = None
    if len(calibration_params.obj_points) > 0 and len(calibration_params.image_points) > 0:
        status, camera_matrix, distortion, r_vectors, t_vectors = \
            cv2.calibrateCamera(calibration_params.obj_points, calibration_params.image_points,
                               (image_w, image_h), None, None)
        calib_results = CameraCalibrationInfo(camera_matrix, distortion, t_vectors, r_vectors) if status else None
    return calib_results


def _save_to_file(file_path: str, any_file):
    assert isinstance(file_path, str)
    with open(file_path, 'wt', encoding='utf-8') as output_file:
        print(str(any_file), file=output_file, end='')


def save_camera_calib_args(file_path: str, calib_args: CameraCalibrationArgs):
    assert isinstance(calib_args, CameraCalibrationArgs)
    _save_to_file(file_path, calib_args)


def save_camera_calib_info(file_path: str, calib_info: CameraCalibrationInfo):
    assert isinstance(calib_info, CameraCalibrationInfo)
    _save_to_file(file_path, calib_info)


def undistort_image(image: np.ndarray, camera_calibration_info: CameraCalibrationInfo) -> np.ndarray:
    """
    :param image: изображение,дисторсию на котором требуется скомпенсировать.
    :param camera_calibration_info: параметры для компенсации дисторсии.
    :return:
    """
    h, w = image.shape[0], image.shape[1]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_calibration_info.camera_matrix,
                                                           camera_calibration_info.distortion_coefficients,
                                                           (w, h), 1, (w, h))
    # undistorted image
    undistorted_image = cv2.undistort(image, camera_calibration_info.camera_matrix,
                                      camera_calibration_info.distortion_coefficients,
                                      None, new_camera_matrix)
    # crop the image
    x, y, w, h = roi
    undistorted_image = undistorted_image[y: y + h, x: x + w]
    # resize the image
    undistorted_image = cv2.resize(undistorted_image, (w, h), interpolation=cv2.INTER_AREA)
    return undistorted_image


# if __name__ == "__main__":
#     calib_args = CameraCalibrationArgs(ches_board_size=(6, 9))
#     # save_camera_calib_args('calibration_args.json', calib_args)
#     # print(load_camera_calib_args('calibration_args.json'))
#     # calib_info = load_camera_calib_info("calibration_results.json")
#     # print(calib_info)
#     # exit()
#     calib_info = compute_camera_calibration_data("raspimg", calib_args, n_images=10)
#     if calib_info is None:
#         print('Calibration failed')
#     save_camera_calib_info('calibration_results.json', calib_info)
#     # with open('calibration_results.json', 'wt', encoding='utf-8') as output_file:
#    #     print(calib_info, file=output_file, end='')


