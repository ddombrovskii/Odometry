import os
from collections import namedtuple
from typing import List, Tuple, Dict, Union
import random

import numpy as np
import json


def read_students(file_path: str) -> List[Tuple[str, str, int, int]]:
    students = []
    with open(file_path, 'rt', encoding='utf-8') as file:
        for line in file:
            try:
                splitted_line = line.split(' ')
                student = (splitted_line[0], splitted_line[1], int(splitted_line[2]), int(splitted_line[3]))
                students.append(student)
            except ValueError as er:
                continue
            except IndexError as er:
                continue
    return students


def create_csv_file(students_file_path: str, students: List[Tuple[str, str, int, int]]) -> bool:
    assert isinstance(students_file_path, str)
    assert len(students_file_path) != 0
    if len(students) == 0:
        return False
    students_file_path = students_file_path if students_file_path.endswith('csv') else f"{students_file_path}.csv"
    with open(students_file_path, "wt", encoding='utf-8') as output_file:
        print("name;surname;group;subgroup;date;presence;lab_work_number;lab_work_mark;", file=output_file)
        for lab_work_n in range(4):
            for student in students:
                print(
                    f"\"{student[0]}\";\"{student[1]}\";{student[2]};{student[3]};"
                    f"\"15:{9 + lab_work_n}:23\";1;{lab_work_n};{int(random.uniform(2,5))};",
                    file=output_file)
    return True


def create_json_file(students_file_path: str, students: List[Tuple[str, str, int, int]]) -> bool:
    assert isinstance(students_file_path, str)
    assert len(students_file_path) != 0
    if len(students) == 0:
        return False
    students_file_path = students_file_path if students_file_path.endswith('json') else f"{students_file_path}.json"
    # students_packed: Dict[Tuple[str, str], List[Tuple[int, int]]] = {}
    # for student in students:
    #     key = student[0:2]
    #     if key in students_packed:
    #         students_packed[key].append(student[2:4])
    #         continue
    #     students_packed.update({key: student[2:4]})

    with open(students_file_path, "wt", encoding='utf-8') as output_file:
        print("{\n\"students\":[\n", file=output_file)
        for student_id, student in enumerate(students):
            print(f"\t{{\n"
                  f"\t\"name\":    \"{student[0]}\",\n"
                  f"\t\"surname\": \"{student[1]}\",\n"
                  f"\t\"group\":   {student[2]},\n"
                  f"\t\"subgroup\":{student[3]},\n"
                  f"\t\"lab_works_sessions\":[\n"
                  f"\t{{\n"
                  f"\t\t\"date\":          \"15:09:23\",\n"
                  f"\t\t\"presence\":      1,\n"
                  f"\t\t\"lab_work_n\":    1,\n"
                  f"\t\t\"lab_work_mark\": {int(random.uniform(2,5))}\n"
                  f"\t}},\n"
                  f"\t{{\n"
                  f"\t\t\"date\":          \"15:10:23\",\n"
                  f"\t\t\"presence\":      1,\n"
                  f"\t\t\"lab_work_n\":    2,\n"
                  f"\t\t\"lab_work_mark\": {int(random.uniform(2,5))}\n"
                  f"\t}},\n"
                  f"\t{{\n"
                  f"\t\t\"date\":          \"15:11:23\",\n"
                  f"\t\t\"presence\":      1,\n"
                  f"\t\t\"lab_work_n\":    3,\n"
                  f"\t\t\"lab_work_mark\": {int(random.uniform(2,5))}\n"
                  f"\t}},\n"
                  f"\t{{\n"
                  f"\t\t\"date\":          \"15:12:23\",\n"
                  f"\t\t\"presence\":      1,\n"
                  f"\t\t\"lab_work_n\":    4,\n"
                  f"\t\t\"lab_work_mark\": {int(random.uniform(2,5))}\n"
                  f"\t}}]\n"
                  f"\t}}", file=output_file, end='')
            if student_id != len(students) - 1:
                print(",\n", file=output_file, end='')
        print("]\n}\n", file=output_file, end='')
    return True


# список всех ключей для валидации json ноды при чтении
JSON_NODE_ALL_KEYS =\
    {"front_img",
     "right_img",
     "back_img",
     "left_img",
     "front_transform",
     "right_transform",
     "back_transform",
     "left_transform"}

# список только строковых
JSON_NODE_PATHS_KEYS =\
    {"front_img",
     "right_img",
     "back_img",
     "left_img"}

# список только np.ndarray
JSON_NODE_TRANSFORMS_KEYS =\
    {"front_transform",
     "right_transform",
     "back_transform",
     "left_transform"}


class ViewInfo(namedtuple('ViewInfo', 'front_img, right_img, back_img, left_img,'
                                      ' front_transform, right_transform, back_transform, left_transform')):
    def __new__(cls, front_img: str, right_img: str, back_img: str, left_img: str,
                front_transform: np.ndarray, right_transform: np.ndarray,
                back_transform: np.ndarray, left_transform: np.ndarray):
        return super().__new__(cls, front_img, right_img, back_img, left_img,
                               front_transform, right_transform, back_transform, left_transform)

    def __str__(self):
        return f"{{\n" \
               f"\t\"front_img\":       \"{self.front_img}\",\n" \
               f"\t\"right_img\":       \"{self.right_img}\",\n" \
               f"\t\"back_img\":        \"{self.back_img}\",\n" \
               f"\t\"left_img\":        \"{self.left_img}\",\n" \
               f"\t\"front_transform\": [{', '.join(str(v) for v in self.front_transform.flat)}],\n" \
               f"\t\"right_transform\": [{', '.join(str(v) for v in self.right_transform.flat)}],\n" \
               f"\t\"back_transform\":  [{', '.join(str(v) for v in self.back_transform.flat)}],\n" \
               f"\t\"left_transform\":  [{', '.join(str(v) for v in self.left_transform.flat)}]\n" \
               f"}}"


def _read_view_info(json_node):
    # node validation
    for key in JSON_NODE_ALL_KEYS:
        if key not in json_node:
            raise KeyError(f'key \"{key}\" does not present in json_node...')
    for key in JSON_NODE_PATHS_KEYS:
        if len(json_node[key]) == 0:
            raise ValueError(f'empy path \"{key}\"...')
    for key in JSON_NODE_TRANSFORMS_KEYS:
        if len(json_node[key]) != 16:
            raise IndexError(f'incorrect transform \"{key}\"...')
    # node parsing
    # float(v) may cause ValueError...
    transforms = [np.array([float(v) for v in json_node[key]]).reshape(4, 4) for key in JSON_NODE_TRANSFORMS_KEYS]
    views = [json_node[key] for key in JSON_NODE_PATHS_KEYS]
    return ViewInfo(*views, *transforms)


def read_views_info(path_2_file: str) -> Union[List[ViewInfo], None]:
    if not os.path.exists(path_2_file):
        return None
    with open(path_2_file, 'rt') as input_file:
        raw_data = json.load(input_file)
        if "views" not in raw_data:
            return None
        views = []
        for node in raw_data["views"]:
            try:
                views.append(_read_view_info(node))
            except KeyError as er:
                print(er)
                continue
            except ValueError as er:
                print(er)
                continue
            except IndexError as er:
                print(er)
                continue
        return views


def xor(left: int, right: int) -> int:
    return (left & ~right) | (~left & right)


def half_adder(left: int, right: int) -> Tuple[int, int]:
    return xor(left, right), left & right


def full_adder(left: int, right: int, carray_in: int) -> Tuple[int, int]:
    summ_1, carry_1 = half_adder(left, right)
    summ_2, carry_2 = half_adder(summ_1, carray_in)
    return summ_2, carry_1 | carry_2


def is_bit_set(bytes_: int, bit_: int) -> bool:
    return (bytes_ & (1 << bit_)) != 0


INT_BITS_COUNT = 32


def int_to_bin(value: int) -> Tuple[int, ...]:
    return tuple(1 if is_bit_set(value, i) else 0 for i in range(INT_BITS_COUNT))


def bin_to_int(values) -> int:
    return sum(2 ** index for index, bit in enumerate(values) if bit != 0)


def adder(left: int, right: int) -> int:
    carry = 0
    summ_res = []
    for lft, rgt in zip(int_to_bin(left), int_to_bin(right)):
        summ, carry = full_adder(lft, rgt, carry)
        summ_res.append(summ)
    return bin_to_int(summ_res)  # sum(2 ** index for index, bit in enumerate(summ_res) if bit != 0)


def _adder(left: Tuple[int, ...], right: Tuple[int, ...]) -> Tuple[int, ...]:
    carry = 0
    summ_res = []
    for lft, rgt in zip(left, right):
        summ, carry = full_adder(lft, rgt, carry)
        summ_res.append(summ)
    return tuple(summ_res)


def multiplicator(left: int, right: int) -> int:
    l_bin = int_to_bin(left)
    r_bin = int_to_bin(right)
    m_bin = int_to_bin(0)
    for shift in range(INT_BITS_COUNT):
        _mul  = int_to_bin(bin_to_int(tuple(r_bin[shift] & v for v in l_bin)) << shift)
        m_bin = _adder(m_bin, _mul)
    return bin_to_int(m_bin)


if __name__ == "__main__":
    print(f"X XOR Y | Z\n"
          f"1     1 | {xor(1, 1)}\n"
          f"1     0 | {xor(1, 0)}\n"
          f"0     1 | {xor(0, 1)}\n"
          f"0     0 | {xor(0, 0)}")
    print(f"33 + 19 = {122 + 19:6} => adder(33, 19)         = {adder(122, 19):6}")
    print(f"33 * 19 = {122 * 19:6} => multiplicator(33, 19) = {multiplicator(122, 19):6}")

