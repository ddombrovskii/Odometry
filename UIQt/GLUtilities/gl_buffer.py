from UIQt.GLUtilities.gl_decorators import gl_error_catch
from UIQt.GLUtilities.objects_pool import ObjectsPool
from OpenGL.GL import *
import numpy as np
# Буфер данных на GPU
# Изменение размера
# загрузка в GPU и чтение из GPU


class BufferGL:
    # MAX_BUFFER_AVAILABLE_SIZE: int = ???
    buffers = ObjectsPool()

    __slots__ = "_id", "_bind_target", "_usage_target", "_filling", "_capacity", "_name", "_item_byte_size"

    def __init__(self, cap: int,
                 item_b_size: int = 4,
                 bind_target: GLenum = GL_ARRAY_BUFFER,
                 usage_target: GLenum = GL_STATIC_DRAW):
        self._id: int = 0
        self._bind_target: GLenum = bind_target
        self._usage_target: GLenum = usage_target
        self._filling: int = 0
        self._capacity: int = cap
        self._item_byte_size: int = item_b_size
        self._name = ""
        self._create()

    def __str__(self):
        data = self.read_back_data()
        return f"{{\n" \
               f"\t\"name \"         :\"{self.name}\",\n" \
               f"\t\"bind_id\"       :{self.bind_id},\n" \
               f"\t\"capacity \"     :{self.capacity},\n" \
               f"\t\"filling\"       :{self.filling},\n" \
               f"\t\"item_byte_size\":{self.item_byte_size},\n" \
               f"\t\"bind_target\"   :{int(self.bind_target)},\n" \
               f"\t\"usage_target\"  :{int(self.usage_target)},\n"\
               f"\t\"data\"          :[{','.join(f'{str(v)}' for v in data)}]\n}}"

    def __del__(self):
        self.delete()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    @gl_error_catch
    def _create(self) -> None:
        self._id = glGenBuffers(1)
        self.bind()
        glBufferData(self.bind_target, self.capacity * self.item_byte_size, None, self.usage_target)
        self._name = f"gl_buffer_{self.bind_id}"
        BufferGL.buffers.register_object(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def bind_target(self) -> GLenum:
        return self._bind_target

    @property
    def usage_target(self) -> GLenum:
        return self._usage_target

    @property
    def filling(self) -> int:
        return self._filling

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def item_byte_size(self) -> int:
        return self._item_byte_size

    @property
    def bind_id(self) -> int:
        return self._id

    def bind(self) -> None:
        if not BufferGL.buffers.bounded_update(self.bind_id):
            return
        glBindBuffer(self.bind_target, self.bind_id)

    def unbind(self) -> None:
        glBindBuffer(self.bind_target, 0)
        BufferGL.buffers.bounded_update(0)

    @gl_error_catch
    def delete(self) -> None:
        if self.bind_id == 0:
            return
        BufferGL.buffers.unregister_object(self)
        glDeleteBuffers(1, np.ndarray([self.bind_id]))
        self._id = 0
        self._filling = 0
        self._capacity = 0

    @gl_error_catch
    def read_back_data(self, start_element: int = None, elements_number: int = None) -> np.ndarray:
        if start_element is None:
            start_element = 0

        if elements_number is None:
            elements_number = self.capacity

        if start_element + elements_number > self.capacity:
            return np.zeros((1, 1), dtype=np.float32)

        self.bind()
        # b_data = np.zeros((1, elements_number), dtype=np.float32)
        b_data = glGetBufferSubData(self.bind_target, self.item_byte_size * start_element,
                                    self.item_byte_size * elements_number)
        # print(b_data.astype('<f4'))
        if self.bind_target == GL_ELEMENT_ARRAY_BUFFER:
            return b_data.view('<i4')
        if self.bind_target == GL_ARRAY_BUFFER:
            return b_data.view('<f4')
        return b_data

    @gl_error_catch
    def resize(self, new_size: int) -> None:
        if self.capacity == new_size:
            return
        if new_size <= 0:
            return
        self.bind()
        if self.filling == 0:
            self.delete()
            self._capacity = new_size
            self._create()
            return
        bid = glGenBuffers(1)
        glBindBuffer(self.bind_target, bid)
        glBufferData(self.bind_target, new_size * self.item_byte_size, ctypes.c_int(0), self.usage_target)
        glBindBuffer(GL_COPY_READ_BUFFER, self.bind_id)
        glBindBuffer(GL_COPY_WRITE_BUFFER, bid)
        if self.filling > new_size:
            self._filling = new_size
        glCopyBufferSubData(GL_COPY_READ_BUFFER, GL_COPY_WRITE_BUFFER, 0, 0, self.filling * self.item_byte_size)
        self.delete()
        self._id = bid
        self._capacity = new_size
        self._filling = new_size
        BufferGL.buffers.register_object(self)

    def load_buffer_data(self, data: np.ndarray) -> None:
        self.load_buffer_sub_data(0, data)

    @gl_error_catch
    def load_buffer_sub_data(self, start_offset, data: np.ndarray) -> None:
        self.bind()
        if len(data) > self.capacity - start_offset:
            self.resize(len(data) + start_offset)
        glBufferSubData(self.bind_target, start_offset * self.item_byte_size, len(data) * self.item_byte_size, data)
        err_code = glGetError()

        if err_code != GL_NO_ERROR:
            print(f"Error buffer data loading: {err_code}")
        self._filling += len(data)
        if self.filling > self.capacity:
            self._filling = self.capacity
