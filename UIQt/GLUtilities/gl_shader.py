from ctypes import addressof, POINTER, cast, c_float, c_ubyte, Structure
from Utilities.Geometry import Matrix4, Matrix3, Vector3, Vector2
from OpenGL.GL.shaders import compileProgram, compileShader
from UIQt.GLUtilities.gl_objects_pool import ObjectsPoolGL
from UIQt.GLUtilities.gl_decorators import gl_error_catch
from collections import namedtuple
from typing import Dict
from OpenGL.GL import *
import re


class UniformBuffer:

    def __init__(self, program_id, block_name, index, size):
        self.program_id = program_id
        self.block_name = block_name
        self.index = index
        self.size = size
        self._uniforms = self.parse_all_uniforms()

    def parse_all_uniforms(self):
        # Query the number of active Uniforms:
        num_active = GLint()
        indices = (GLuint * num_active.value)()
        indices_ptr = cast(addressof(indices), POINTER(GLint))
        glGetActiveUniformBlockiv(self.program_id, self.index, GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS, num_active)
        glGetActiveUniformBlockiv(self.program_id, self.index, GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES, indices_ptr)

        # Create objects and pointers for query values:
        offsets = (GLint * num_active.value)()
        gl_types = (GLuint * num_active.value)()
        offsets_ptr = cast(addressof(offsets), POINTER(GLint))
        gl_types_ptr = cast(addressof(gl_types), POINTER(GLint))

        # Query the indices, offsets, and types uniforms:
        glGetActiveUniformsiv(self.program_id, num_active.value, indices, GL_UNIFORM_OFFSET, offsets_ptr)
        glGetActiveUniformsiv(self.program_id, num_active.value, indices, GL_UNIFORM_TYPE, gl_types_ptr)

        # Get the uniform block member names
        # TODO: Make sure that the indices are valid!
        names = []
        for index in range(num_active.value):
            buf_size = 192
            uname = ctypes.create_string_buffer(buf_size)
            usize = GLint()
            utype = GLenum()

            glGetActiveUniform(self.program_id, index, buf_size, None, usize, utype, uname)
            name = uname.value.decode().split('.')[1]
            # Names will be listed as '{Structure}.{field}',
            # therefore we must split them at the dot and keep the right side
            names.append(name)

        return offsets, gl_types, names

    def create_view(self):
        # Utility function to print ctypes Structure as python dict
        repr_fn = lambda self: repr({n: v for n, v in [(n[0], getattr(self, n[0])) for n in self._fields_]})

        args = []  # List of the view arguments
        count = 1  # For naming padding fields
        last_offset = -1  # Used to detect places where padding is necessary
        last_type_size = -1  # Used to detect places where padding is necessary

        for offset, gl_type, name in zip(self._uniforms[0], self._uniforms[1], self._uniforms[2]):
            # TODO map the remaining types ( http://docs.gl/gl3/glGetActiveUniformsiv )
            gl_type_map = {GL_FLOAT: c_float}

            ctypes_type = gl_type_map[gl_type]
            sizeof_ctypes_type = sizeof(ctypes_type)

            # Check if padding bytes must be added between fields.
            local_offset = last_offset + last_type_size
            if last_offset != -1 and local_offset != offset:
                padding_bytes_count = offset - last_offset - last_type_size
                args.append(('padding' + str(count), c_ubyte * padding_bytes_count))
                # Add the padding field to the ctype struct
                count += 1

            # Add the new field to the ctype struct
            args.append((name, ctypes_type))

            last_offset = offset
            last_type_size = sizeof_ctypes_type

        view = type(self.name + 'View', (Structure,), {'_fields_': args, '__repr__': repr_fn})

        return view

    def __repr__(self):
        return "{0}(name={1})".format(self.__class__.__name__, self.name)


class ShaderUniform(namedtuple("ShaderUniform", "uniform_name, uniform_location, data_type, data_size")):
    def __new__(cls, uniform_name: str, uniform_location: int, data_type: int, data_size: int):
        return super().__new__(cls, uniform_name, uniform_location, data_type, data_size)

    def __str__(self):
        return f"{{\n" \
               f"\t\"uniform_name\"     : \"{self.uniform_name}\"," \
               f"\t\"uniform_location\" : {self.uniform_location}," \
               f"\t\"data_type\"        : {self.data_type}," \
               f"\t\"data_size\"        : {self.data_size}" \
               f"\n}}"


class ShaderAttribute(namedtuple("ShaderAttribute", "attribute_name, attribute_location, data_type, data_size")):
    def __new__(cls, attribute_name: str, attribute_location: int, data_type: int, data_size: int):
        return super().__new__(cls, attribute_name, attribute_location, data_type, data_size)

    def __str__(self):
        return f"{{\n" \
               f"\t\"attribute_name\"     : \"{self.attribute_name}\"," \
               f"\t\"attribute_location\" : {self.attribute_location}," \
               f"\t\"data_type\"          : {self.data_type}," \
               f"\t\"data_size\"          : {self.data_size}" \
               f"\n}}"
               

class ShaderGL:
    Matrix_4: int = 35676
    Matrix_3: int = 35675
    Vector_4: int = 35666
    Vector_3: int = 35665
    Vector_2: int = 35664
    Float: int = 5126
    Int: int = 5124
    Bool: bool = 35670
    Texture: int = 35678
    TextureCube: int = 35680
    TextureArray: int = 36289

    UniformTypes = \
        {
            Matrix_4: Matrix_4,
            Matrix_3: Matrix_3,
            Vector_3: Vector_3,
            Vector_2: Vector_2,
            Float: Float,
            Int: Int,
            Bool: Bool,
            Texture: Texture,
            TextureCube: TextureCube,
            TextureArray: TextureArray
        }

    UniformTypesNames = \
        {
            Matrix_4: '\"Matrix_4\"',
            Matrix_3: '\"Matrix_3\"',
            Vector_3: '\"Vector_3\"',
            Vector_2: '\"Vector_2\"',
            Float: '\"Float\"',
            Int: '\"Int\"',
            Bool: '\"Bool\"',
            Texture: '\"Texture\"',
            TextureCube: '\"TextureCube\"',
            TextureArray: '\"TextureArray\"'
        }

    shaders = ObjectsPoolGL()

    @staticmethod
    def _read_all_code(code_src: str) -> str:
        with open(code_src, mode='r') as file:
            code = ''.join((re.sub(r"\t*", "", line)) for line in file)
            if len(code) == 0:
                raise Exception("Vertex shader creation error::empty src-code...")
            return code

    @staticmethod
    def gl_get_active_attrib(program, index):
        buf_size = 256
        length = (ctypes.c_int * 1)()
        size = (ctypes.c_int * 1)()
        attrib_type = (ctypes.c_uint * 1)()
        attrib_name = ctypes.create_string_buffer(buf_size)
        # pyopengl has a bug, this is a patch
        glGetActiveAttrib(program, index, buf_size, length, size, attrib_type, attrib_name)
        attrib_name = attrib_name[:length[0]].decode('utf-8')
        return attrib_name, size[0], attrib_type[0]

    @staticmethod
    def gl_get_active_uniform(program, index):
        buf_size = 256
        length = (ctypes.c_int * 1)()
        size = (ctypes.c_int * 1)()
        attrib_type = (ctypes.c_uint * 1)()
        attrib_name = ctypes.create_string_buffer(buf_size)
        glGetActiveUniform(program, index, buf_size, length, size, attrib_type, attrib_name)
        attrib_name = attrib_name[:length[0]].decode('utf-8')
        return attrib_name, size[0], attrib_type[0]

    @staticmethod
    def gl_get_active_uniform_block(program, index):
        buf_size = 256
        length = (ctypes.c_int * 1)()
        size = (ctypes.c_int * 1)()
        block_type = (ctypes.c_uint * 1)()
        block_name = ctypes.create_string_buffer(buf_size)
        glGetActiveUniformBlockName(program, index, buf_size, size, block_name)
        block_name = block_name[:length[0]].decode('utf-8')
        return block_name, size[0], block_type[0]

    def __init__(self):
        # todo name
        self._name: str = ""
        self._program_id: int = 0
        self._vert_id: int = 0
        self._frag_id: int = 0
        self._vert_src: str = ""
        self._frag_src: str = ""

        # uniforms
        self._shader_uniforms_by_name: Dict[str, ShaderUniform] = {}
        self._shader_uniforms_by_id: Dict[int, ShaderUniform] = {}

        # attributes
        self._shader_attributes_by_name: Dict[str, ShaderAttribute] = {}
        self._shader_attributes_by_id: Dict[int, ShaderAttribute] = {}

        # uniform_blocks
        self._shader_uniform_blocks: dict = {}

    def __str__(self):
        def comas(_name):
            return f"\"{_name}\""

        def parce(_name, _id, _type, _size):
            return f"{{ \"name\": {comas(_name):20}, \"id\": {_id:3}," \
                   f" \"size\": {_size:3}, \"type\": {ShaderGL.UniformTypesNames[_type]:12}}}"

        separator = ',\n\t\t'
        return f"{{\n" \
               f"\t//Shader     : 0x{id(self)}\n" \
               f"\t\"name\"       : \"{self._name}\",\n" \
               f"\t\"program_id\" : {self.bind_id},\n" \
               f"\t\"vert_id\"    : {self.vert_id},\n" \
               f"\t\"frag_id\"    : {self.frag_id},\n" \
               f"\t\"attributes\" : \n\t[\n\t\t" \
               f"{separator.join(parce(*v) for v in self.attributes.values())}" \
               f"\n\t],\n" \
               f"\t\"uniforms\" : \n\t[\n\t\t" \
               f"{separator.join(parce(*v) for v in self.uniforms.values())}" \
               f"\n\t]\n" \
               f"}}"

    def __del__(self):
        self.delete()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    @gl_error_catch
    def delete(self):
        if self.bind_id == 0:
            return
        glDeleteShader(self._vert_id)
        glDeleteShader(self._frag_id)
        glDeleteProgram(self.bind_id)
        ShaderGL.shaders.unregister_object(self)
        self._program_id = 0
        self._vert_id = 0
        self._frag_id = 0

    @property
    def attributes(self) -> Dict[str, ShaderAttribute]:
        return self._shader_attributes_by_name

    @property
    def uniforms(self) -> Dict[str, ShaderUniform]:
        return self._shader_uniforms_by_name

    @property
    def attributes_by_id(self) -> Dict[int, ShaderAttribute]:
        return self._shader_attributes_by_id

    @property
    def uniforms_by_id(self) -> Dict[int, ShaderUniform]:
        return self._shader_uniforms_by_id

    @property
    def name(self):
        return self._name

    @property
    def bind_id(self) -> int:
        return self._program_id

    @property
    def frag_id(self) -> int:
        return self._frag_id

    @property
    def vert_id(self) -> int:
        return self._vert_id

    @property
    def frag_src(self) -> str:
        return self._frag_src

    @property
    def vert_src(self) -> str:
        return self._vert_src

    def get_uniform_location(self, uniform_name: str):
        return self._shader_uniforms_by_name[uniform_name].uniform_location \
            if uniform_name in self._shader_uniforms_by_name else -1

    def get_attrib_location(self, attrib_name: str):
        return self._shader_attributes_by_name[attrib_name].attribute_location\
            if attrib_name in self._shader_attributes_by_name else -1

    def get_uniform_location_by_id(self, uniform_id: int):
        return uniform_id if uniform_id in self._shader_uniforms_by_id else -1

    def get_attrib_location_by_id(self, attrib_id: str):
        return attrib_id if attrib_id in self._shader_attributes_by_id else -1

    @gl_error_catch
    def _get_all_attrib_locations(self):
        count = glGetProgramiv(self.bind_id, GL_ACTIVE_ATTRIBUTES)
        if len(self._shader_attributes_by_name) != 0:
            self._shader_attributes_by_name.clear()
            self._shader_attributes_by_id.clear()
        for i in range(count):
            name_, size_, type_ = ShaderGL.gl_get_active_attrib(self.bind_id, i)
            attribute = ShaderAttribute(name_, i, type_, size_)
            self._shader_attributes_by_name.update({name_: attribute})
            self._shader_attributes_by_id.update({i: attribute})

    # @gl_error_catch
    # def _get_all_uniform_blocks(self):
    #     count = glGetProgramiv(self.bind_id, GL_ACTIVE_UNIFORM_BLOCKS)
    #     if len(self._shader_uniform_blocks) != 0:
    #         self._shader_uniform_blocks.clear()
    #     for i in range(count):
    #         name_, size_, type_ = ShaderGL.gl_get_active_uniform_block(self.bind_id, i)
    #         self._shader_uniform_blocks[name_] = (i, size_, type_)

    @gl_error_catch
    def _get_all_uniform_locations(self):
        count = glGetProgramiv(self.bind_id, GL_ACTIVE_UNIFORMS)
        if len(self._shader_uniforms_by_name) != 0:
            self._shader_uniforms_by_name.clear()
            self._shader_uniforms_by_id.clear()
        for i in range(count):
            name_, size_, type_ = ShaderGL.gl_get_active_uniform(self.bind_id, i)
            uniform = ShaderUniform(name_, i, type_, size_)
            self._shader_uniforms_by_name.update({name_: uniform})
            self._shader_uniforms_by_id.update({i: uniform})

    def load_defaults_settings(self):
        for name_ in self._shader_uniforms_by_name:
            uniform: ShaderUniform = self._shader_uniforms_by_name[name_]
            if uniform.data_type not in ShaderGL.UniformTypes:
                continue
            if ShaderGL.Matrix_4 == uniform.data_type:
                self.send_mat_4(name_, Matrix4.identity())
                continue
            if ShaderGL.Matrix_3 == uniform.data_type:
                self.send_mat_3(name_, Matrix3.identity())
                continue
            if ShaderGL.Vector_3 == uniform.data_type:
                self.send_vec_3(name_, Vector3(1, 1, 1))
                continue
            if ShaderGL.Vector_2 == uniform.data_type:
                self.send_vec_2(name_, Vector2(1, 1))
                continue
            if ShaderGL.Float == uniform.data_type:
                self.send_float(name_, 0.0)
                continue
            if ShaderGL.Int == uniform.data_type:
                self.send_int(name_, 0)
                continue

    @gl_error_catch
    def frag_shader(self, code: str, from_file: bool = True):
        if from_file:
            self._frag_id = compileShader(self._read_all_code(code), GL_FRAGMENT_SHADER)
            if self.frag_id == 0:
                raise Exception(f"{GL_FRAGMENT_SHADER} shader compilation error...")
            self._frag_src = code
            self._compile()
            return
        self._frag_id = compileShader(code, GL_FRAGMENT_SHADER)
        if self.frag_id == 0:
            raise Exception(f"{GL_FRAGMENT_SHADER} shader compilation error...")
        self._compile()

    @gl_error_catch
    def vert_shader(self, code: str, from_file: bool = True):
        if from_file:
            self._vert_id = compileShader(self._read_all_code(code), GL_VERTEX_SHADER)
            if self.vert_id == 0:
                raise Exception(f"{GL_VERTEX_SHADER} shader compilation error...")
            self._vert_src = code
            self._compile()
            return
        self._vert_id = compileShader(code, GL_VERTEX_SHADER)
        if self.vert_id == 0:
            raise Exception(f"{GL_VERTEX_SHADER} shader compilation error...")
        self._compile()

    @gl_error_catch
    def _compile(self):
        if self.vert_id == 0:
            return
        if self.frag_id == 0:
            return
        if self.bind_id != 0:
            self.delete()
        self._program_id = compileProgram(self.vert_id, self.frag_id)
        if self.bind_id == 0:
            raise Exception("Shader program compilation error...")
        self.bind()
        # self._get_all_uniform_blocks()
        self._get_all_attrib_locations()
        self._get_all_uniform_locations()

        if self.frag_src == "" and self.vert_src == "":
            self._name = f"gl_shader_{self.bind_id}"
            ShaderGL.shaders.register_object(self)
            return
        frag_src = self.frag_src.split('.')[-2]
        vert_src = self.vert_src.split('.')[-2]
        if frag_src != vert_src:
            self._name = f"gl_shader_{self.bind_id}"
            ShaderGL.shaders.register_object(self)
            return
        vert_src = vert_src.split('/')[-1]
        self._name = vert_src
        ShaderGL.shaders.register_object(self)

    def bind(self):
        if ShaderGL.shaders.bounded_update(self.bind_id):
            glUseProgram(self.bind_id)

    def unbind(self):
        ShaderGL.shaders.bounded_update(0)
        glUseProgram(0)

    @gl_error_catch
    def send_mat_3(self, mat_name: str, mat: Matrix3, transpose=GL_FALSE):
        loc = self.get_uniform_location(mat_name)
        if loc == -1:
            return
        self.bind()
        glUniformMatrix3fv(loc, 1, transpose, (GLfloat * 9)(*mat))

    @gl_error_catch
    def send_mat_4(self, mat_name: str, mat: Matrix4, transpose=GL_FALSE):
        loc = self.get_uniform_location(mat_name)
        if loc == -1:
            return
        self.bind()
        glUniformMatrix4fv(loc, 1, transpose, (GLfloat * 16)(*mat))

    @gl_error_catch
    def send_vec_2(self, vec_name: str, vec: Vector2):
        loc = self.get_uniform_location(vec_name)
        if loc == -1:
            return
        self.bind()
        glUniform2fv(loc, 1, (GLfloat * 2)(*vec))

    @gl_error_catch
    def send_vec_3(self, vec_name: str, vec: Vector3):
        loc = self.get_uniform_location(vec_name)
        if loc == -1:
            return
        self.bind()
        glUniform3fv(loc, 1, (GLfloat * 3)(*vec))

    @gl_error_catch
    def send_float(self, param_name: str, val: float):
        loc = self.get_uniform_location(param_name)
        if loc == -1:
            return
        self.bind()
        glUniform1f(loc, GLfloat(val))

    @gl_error_catch
    def send_int(self, param_name: str, val: int):
        loc = self.get_uniform_location(param_name)
        if loc == -1:
            return
        self.bind()
        glUniform1i(loc, GLint(val))

    @gl_error_catch
    def send_mat_3_by_id(self, uniform_id: int, mat: Matrix3, transpose=GL_FALSE):
        if uniform_id not in self._shader_uniforms_by_id:
            return
        self.bind()
        glUniformMatrix3fv(uniform_id, 1, transpose, (GLfloat * 9)(*mat))

    @gl_error_catch
    def send_mat_4_by_id(self, uniform_id: int, mat: Matrix4, transpose=GL_FALSE):
        if uniform_id not in self._shader_uniforms_by_id:
            return
        self.bind()
        glUniformMatrix4fv(uniform_id, 1, transpose, (GLfloat * 16)(*mat))

    @gl_error_catch
    def send_vec_2_by_id(self, uniform_id: int, vec: Vector2):
        if uniform_id not in self._shader_uniforms_by_id:
            return
        self.bind()
        glUniform2fv(uniform_id, 1, (GLfloat * 2)(*vec))

    @gl_error_catch
    def send_vec_3_by_id(self, uniform_id: int, vec: Vector3):
        if uniform_id not in self._shader_uniforms_by_id:
            return
        self.bind()
        glUniform3fv(uniform_id, 1, (GLfloat * 3)(*vec))

    @gl_error_catch
    def send_float_by_id(self, uniform_id: int, val: float):
        if uniform_id not in self._shader_uniforms_by_id:
            return
        self.bind()
        glUniform1f(uniform_id, GLfloat(val))

    @gl_error_catch
    def send_int_by_id(self, uniform_id: int, val: int):
        if uniform_id not in self._shader_uniforms_by_id:
            return
        self.bind()
        glUniform1i(uniform_id, GLint(val))
