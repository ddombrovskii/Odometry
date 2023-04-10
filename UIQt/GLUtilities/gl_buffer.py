from OpenGL.GL import *
import numpy as np
# Буфер данных на GPU
# Изменение размера
# загрузка в GPU и чтение из GPU


class BufferGL:
    # MAX_BUFFER_AVAILABLE_SIZE: int = ???
    __buffer_instances = {}

    @staticmethod
    def buffers_write(file, start="", end="") -> None:
        file.write(f"{start}\"buffers\":[\n")
        file.write(',\n'.join(str(buffer) for buffer in BufferGL.__buffer_instances.values()))
        file.write(f"]\n{end}")

    @staticmethod
    def gpu_buffers_enumerate():
        # print(BufferGL.__buffer_instances.items())
        for buffer in BufferGL.__buffer_instances.items():
            yield buffer[1]

    @staticmethod
    def delete_all_gpu_buffers():
        # print(GPUBuffer.__buffer_instances)
        while len(BufferGL.__buffer_instances) != 0:
            item = BufferGL.__buffer_instances.popitem()
            item[1].delete_buffer()

    __slots__ = "__id", "__bind_target", "__usage_target", "__filling", "__capacity", "__item_byte_size"

    def __init__(self, cap: int,
                 item_b_size: int = 4,
                 bind_target: GLenum = GL_ARRAY_BUFFER,
                 usage_target: GLenum = GL_STATIC_DRAW):
        self.__id: int = 0
        self.__bind_target: GLenum = bind_target
        self.__usage_target: GLenum = usage_target
        self.__filling: int = 0
        self.__capacity: int = cap
        self.__item_byte_size: int = item_b_size
        self._create()

    def __str__(self):
        data = self.read_back_data()
        data = np.array2string(data, precision=3, separator=',', suppress_small=True)
        return f"{{\n\t\"unique_id\"     :{self.buffer_id},\n" \
               f"\t\"capacity \"     :{self.capacity},\n" \
               f"\t\"filling\"       :{self.filling},\n" \
               f"\t\"item_byte_size\":{self.item_byte_size},\n" \
               f"\t\"bind_target\"   :{int(self.bind_target)},\n" \
               f"\t\"usage_target\"  :{int(self.usage_target)},\n"\
               f"\t\"data\"          :[{data}]\n}}"

    def __del__(self):
        self.delete_buffer()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def _create(self) -> None:
        try:
            self.__id = glGenBuffers(1)
        except Exception as ex:
            print(f"GPUBuffer creation error:\n{ex.args}")

        self.bind()

        try:
            print(f"buffer cap {self.__capacity}, item size {self.__item_byte_size}")
            glBufferData(self.__bind_target, self.__capacity * self.__item_byte_size,
                         None, self.__usage_target)
        except Exception as ex:
            print(f"GPUBuffer allocation error:\n{ex.args}")
        BufferGL.__buffer_instances.update({self.__id: self})

    @property
    def bind_target(self) -> GLenum:
        return self.__bind_target

    @property
    def usage_target(self) -> GLenum:
        return self.__usage_target

    @property
    def filling(self) -> int:
        return self.__filling

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def item_byte_size(self) -> int:
        return self.__item_byte_size

    @property
    def buffer_id(self) -> int:
        return self.__id

    def bind(self) -> None:
        glBindBuffer(self.__bind_target, self.__id)

    def unbind(self) -> None:
        glBindBuffer(self.__bind_target, 0)

    def delete_buffer(self) -> None:
        if self.__id == 0:
            return
        glDeleteBuffers(1, np.ndarray([self.__id]))
        if self.__id in BufferGL.__buffer_instances:
            del BufferGL.__buffer_instances[self.__id]
        self.__id = 0
        self.__filling = 0
        self.__capacity = 0

    def read_back_data(self, start_element: int = None, elements_number: int = None) -> np.ndarray:
        if start_element is None:
            start_element = 0

        if elements_number is None:
            elements_number = self.capacity

        if start_element + elements_number > self.__capacity:
            return np.zeros((1, 1), dtype=np.float32)

        self.bind()
        # b_data = np.zeros((1, elements_number), dtype=np.float32)
        b_data = glGetBufferSubData(self.__bind_target,
                                    self.__item_byte_size * start_element,
                                    self.__item_byte_size * elements_number)
        # print(b_data.astype('<f4'))
        if self.bind_target == GL_ELEMENT_ARRAY_BUFFER:
            return b_data.view('<i4')
        if self.bind_target == GL_ARRAY_BUFFER:
            return b_data.view('<f4')
        return b_data

    def resize(self, new_size: int) -> None:
        if self.__capacity == new_size:
            return
        if new_size <= 0:
            return
        self.bind()
        if self.__filling == 0:
            self.delete_buffer()
            self.__capacity = new_size
            self._create()
            return
        bid = glGenBuffers(1)
        glBindBuffer(self.__bind_target, bid)
        glBufferData(self.__bind_target, new_size * self.__item_byte_size, ctypes.c_int(0), self.__usage_target)
        glBindBuffer(GL_COPY_READ_BUFFER, self.__id)
        glBindBuffer(GL_COPY_WRITE_BUFFER, bid)
        if self.__filling > new_size:
            self.__filling = new_size
        glCopyBufferSubData(GL_COPY_READ_BUFFER, GL_COPY_WRITE_BUFFER,
                            0, 0, self.__filling * self.__item_byte_size)
        # glDeleteBuffers(1, np.ndarray([self.__id]))
        self.delete_buffer()
        self.__id = bid
        self.__capacity = new_size
        self.__filling = new_size
        BufferGL.__buffer_instances[self.__id] = self

    def load_buffer_data(self, data: np.ndarray) -> None:
        self.load_buffer_sub_data(0, data)

    def load_buffer_sub_data(self, start_offset, data: np.ndarray) -> None:
        self.bind()
        if len(data) > self.__capacity - start_offset:
            self.resize(len(data) + start_offset)
        err_code = glGetError()
        # data_array = (GLfloat * len(data))(*data)
        glBufferSubData(self.__bind_target,
                        start_offset * self.__item_byte_size,
                        len(data) * self.__item_byte_size, data)
        err_code = glGetError()

        if err_code != GL_NO_ERROR:
            print(f"Error buffer data loading: {err_code}")
        self.__filling += len(data)
        if self.__filling > self.__capacity:
            self.__filling = self.__capacity
        # self.unbind()

