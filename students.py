import itertools
import os
from collections import namedtuple
from typing import List, Tuple, Dict, Union
import random

import numpy as np
import json

from Utilities import Timer


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


pairs = ((1, 1), (1, 0), (0, 1), (0, 0))


def xor(left: int, right: int) -> int:
    return (left & ~right) | (~left & right)


def and_truth_table() -> None:
    """
    Таблица истинности для x and y
    """
    nl = '\n'
    print(f"X{'AND':^5}Y | Z\n{nl.join(f'{left}{right:>6} | {left & right}' for left, right in pairs)}")


def or_truth_table() -> None:
    """
    Таблица истинности для x or y
    """
    nl = '\n'
    print(f"X{'OR':^5}Y | Z\n{nl.join(f'{left}{right:>6} | {left | right}' for left, right in pairs)}")


def xor_truth_table() -> None:
    """
    Таблица истинности для x xor y
    """
    nl = '\n'
    print(f"X{'XOR':^5}Y | Z\n{nl.join(f'{left}{right:>6} | {left ^ right}' for left, right in pairs)}")


def half_summator(left: int, right: int) -> Tuple[int, int]:
    return xor(left, right), left & right


def full_summator(left: int, right: int, carray_in: int) -> Tuple[int, int]:
    """
    param left: левый суммируемый бит
    param right: правый суммируемый бит
    param carray_in: бит переноса
    return: значение суммы и бит переноса
    """
    summ_1, carry_1 = half_summator(left, right)
    summ_2, carry_2 = half_summator(summ_1, carray_in)
    return summ_2, carry_1 | carry_2


def _dec_to_bin_generator(value: int):
    """
    Генератор для перевода числа в массив байт.
    """
    while value != 0:
        yield 0 if value % 2 == 0 else 1
        value //= 2


def dec_to_bin(value: int):
    """
    Перевод числа в массив байт.
    """
    return tuple(_dec_to_bin_generator(value))


INT_BITS_COUNT = 32

POWERS_OF_TWO = tuple(2 ** v for v in range(INT_BITS_COUNT))


def bin_to_int(values: Tuple[int, ...]) -> int:
    """
    Перевод массива байт в число.
    """
    return sum(POWERS_OF_TWO[index] for index, bit in enumerate(values) if bit != 0)


def _summator_generator(left: Tuple[int, ...], right: Tuple[int, ...]):
    """
    Генератор каскада суммирования
    """
    carry_bit = 0
    for lft, rgt in itertools.zip_longest(left, right, fillvalue=0):
        summ, carry_bit = full_summator(lft, rgt, carry_bit)
        yield summ
    yield carry_bit


def _summator(left: Tuple[int, ...], right: Tuple[int, ...]) -> Tuple[int, ...]:
    """
    Суммирование двух бинарных чисел
    """
    return tuple(_summator_generator(left, right))


def summator(left: int, right: int) -> int:
    """
    Суммирование двух целых чисел
    """
    return bin_to_int(_summator(dec_to_bin(left), dec_to_bin(right)))


def bin_to_str(bytes_data: Tuple[int, ...]) -> str:
    """
    Строковое представление числа, записанного в виде массива байт.
    """
    return f'0b{"".join(str(v) for v in bytes_data)}'


def multiplicator(left: int, right: int) -> int:
    l_bin = dec_to_bin(left)
    r_bin = dec_to_bin(right)
    m_bin = dec_to_bin(0)
    for shift in range(len(r_bin)):
        t_mul  = dec_to_bin(bin_to_int(tuple(r_bin[shift] & v for v in l_bin)) << shift)
        m_bin = _summator(m_bin, t_mul)
    return bin_to_int(m_bin)


if __name__ == "__main__":
    or_truth_table()
    print()
    and_truth_table()
    print()
    xor_truth_table()
    print()
    first = 121
    second = 1213411
    print(f"{first:^9} + {second:^9} = {first + second:^9} => "
          f"summator     ({first:^9}, {second:^9}) = {summator(first, second):^9}")
    # print(f"{first:^9} * {second:^9} = {first * second:^9} => "
    #       f"multiplicator({first:^9}, {second:^9}) = {multiplicator(first, second):^9}")

