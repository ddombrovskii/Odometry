from ctypes import addressof, POINTER, cast, c_float, c_ubyte, Structure
from Utilities.Geometry import Matrix4, Matrix3, Vector3, Vector2
from OpenGL.GL.shaders import compileProgram, compileShader
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


class Shader:
    Matrix_4: int = 35676
    Matrix_3: int = 35675
    Vector_3: int = 35665
    Vector_2: int = 35664
    Float: int = 5126
    Int: int = 5124
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
            Texture: '\"Texture\"',
            TextureCube: '\"TextureCube\"',
            TextureArray: '\"TextureArray\"'
        }

    __shader_instances = {}

    SAMPLE_SHADER = None

    # UI_TEXT_SHADER = None
    #
    # UI_CLEAR_FB_SHADER = None
    #
    # FRAME_BUFFER_BLIT_SHADER = None

    @staticmethod
    def init_globals():
        Shader.SAMPLE_SHADER = Shader()
        Shader.SAMPLE_SHADER.vert_shader("./GLUtilities/Shaders/sample_shader.vert")
        Shader.SAMPLE_SHADER.frag_shader("./GLUtilities/Shaders/sample_shader.frag")
        Shader.SAMPLE_SHADER.load_defaults_settings()

        #  Shader.FRAME_BUFFER_BLIT_SHADER = Shader()
        #  Shader.FRAME_BUFFER_BLIT_SHADER.vert_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_render_shader.vert")
        #  Shader.FRAME_BUFFER_BLIT_SHADER.frag_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_render_shader.frag")
        #  Shader.FRAME_BUFFER_BLIT_SHADER.load_defaults_settings()

        #  Shader.UI_TEXT_SHADER = Shader()
        #  Shader.UI_TEXT_SHADER.vert_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_text_shaders/ui_text_shader.vert")
        #  Shader.UI_TEXT_SHADER.frag_shader("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_text_shaders/ui_text_shader.frag")
        #  Shader.UI_TEXT_SHADER.load_defaults_settings()

        #  Shader.UI_CLEAR_FB_SHADER = Shader()
        #  Shader.UI_CLEAR_FB_SHADER.vert_shader\
        #      ("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_renderer_region_clean_up_shader.vert")
        #  Shader.UI_CLEAR_FB_SHADER.frag_shader\
        #      ("E:/GitHub/VisualOdometry/UI/gl/shaders/ui_renderer_region_clean_up_shader.frag")
        #  Shader.UI_CLEAR_FB_SHADER.load_defaults_settings()

    @staticmethod
    def shaders_enumerate():
        print(Shader.__shader_instances.items())
        for buffer in Shader.__shader_instances.items():
            yield buffer[1]

    @staticmethod
    def delete_all_shaders():
        # print(GPUBuffer.__buffer_instances)
        while len(Shader.__shader_instances) != 0:
            item = Shader.__shader_instances.popitem()
            item[1].delete_shader()

    # @staticmethod
    # def default_shader():
    #    shader = Shader()
    #    shader.vert_shader(vertex_src, False)
    #    shader.frag_shader(fragment_src, False)
    #    print(shader)
    #    shader.load_defaults_settings()
    #    return shader

    @staticmethod
    def __read_all_code(code_src: str) -> str:
        code: str = ""
        with open(code_src, mode='r') as file:
            for str_ in file:
                line = (re.sub(r"\t*", "", str_))
                code += line
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
        # try:
        # except Exception:
        #     return None

    def __init__(self):
        self.name: str = "default"
        self.__program_id = 0
        self.__vert_id = 0
        self.__frag_id = 0
        self.__shader_uniforms: dict = {}
        self.__shader_uniform_blocks: dict = {}
        self.__shader_attributes: dict = {}

    def __str__(self):
        def comas(_name):
            return f"\"{_name}\""

        def parce(_name, _id, _type, _size):
            return f"{{ \"name\": {comas(_name):20}, \"id\": {_id:3}," \
                   f" \"size\": {_size:3}, \"type\": {Shader.UniformTypesNames[_type]:12}}}"

        separator = ',\n\t\t'
        return f"{{\n" \
               f"\t//Shader       : 0x{id(self)}\n" \
               f"\t\"name\"       : \"{comas(self.name)}\",\n" \
               f"\t\"program_id\" : {self.program_id},\n" \
               f"\t\"vert_id\"    : {self.__vert_id},\n" \
               f"\t\"frag_id\"    : {self.__frag_id},\n" \
               f"\t\"attributes\" : [\n\t\t" \
               f"{separator.join(parce(_name, _id, _type, _size) for _name, (_id, _size, _type) in self.attribytes.items())}" \
               f"\n\t],\n" \
               f"\t\"uniforms\" : [\n\t\t" \
               f"{separator.join(parce(_name, _id, _type, _size) for _name, (_id, _size, _type) in self.uniforms.items())}" \
               f"\n\t]\n" \
               f"}}"

    def __del__(self):
        self.delete_shader()

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def delete_shader(self):
        if self.__program_id == 0:
            return
        glDeleteShader(self.__vert_id)
        glDeleteShader(self.__frag_id)
        glDeleteProgram(self.__program_id)
        if self.__program_id in Shader.__shader_instances:
            del Shader.__shader_instances[self.__program_id]
        self.__program_id = 0
        self.__vert_id = 0
        self.__frag_id = 0

    @property
    def attribytes(self):
        return self.__shader_attributes

    @property
    def uniforms(self):
        return self.__shader_uniforms

    @property
    def program_id(self):
        return self.__program_id

    def get_uniform_location(self, uniform_name: str):
        return self.__shader_uniforms[uniform_name][0] if uniform_name in self.__shader_uniforms else -1

    def get_attrib_location(self, attrib_name: str):
        return self.__shader_attributes[attrib_name][0] if attrib_name in self.__shader_attributes else -1

    def __get_all_uniform_blocks(self):
        count = glGetProgramiv(self.__program_id, GL_ACTIVE_UNIFORM_BLOCKS)
        print(f"Active Uniform Blocks: {count}\n", )
        if len(self.__shader_uniform_blocks) != 0:
            self.__shader_uniform_blocks.clear()
        for i in range(count):
            name_, size_, type_ = Shader.gl_get_active_uniform_block(self.__program_id, i)
            self.__shader_uniform_blocks[name_] = (i, size_, type_)
            print(f"name: {name_:15}, id: {i:3}, size: {size_:3}, type: {type_:5}")

    def __get_all_attrib_locations(self):
        count = glGetProgramiv(self.__program_id, GL_ACTIVE_ATTRIBUTES)
        print(f"\nActive Attributes: {count}\n", )
        if len(self.__shader_attributes) != 0:
            self.__shader_attributes.clear()
        for i in range(count):
            name_, size_, type_ = Shader.gl_get_active_attrib(self.__program_id, i)
            self.__shader_attributes[name_] = (i, size_, type_)
            print(f"name: {name_:15}, id: {i:3}, size: {size_:3}, type: {type_:5}")

    def __get_all_uniform_locations(self):
        count = glGetProgramiv(self.__program_id, GL_ACTIVE_UNIFORMS)
        print(f"\nActive Uniforms: {count}\n")
        if len(self.__shader_uniforms) != 0:
            self.__shader_uniforms.clear()
        for i in range(count):
            name_, size_, type_ = Shader.gl_get_active_uniform(self.__program_id, i)
            self.__shader_uniforms[name_] = (i, size_, type_)
            print(f"name: {name_:15}, id: {i:3}, size: {size_:3}, type: {type_:5}")

    def load_defaults_settings(self):
        for name_ in self.__shader_uniforms:
            type_ = self.__shader_uniforms[name_][2]
            if type_ not in Shader.UniformTypes:
                continue
            if Shader.Matrix_4 == type_:
                self.send_mat_4(name_, Matrix4.identity())
                continue
            if Shader.Matrix_3 == type_:
                self.send_mat_3(name_, Matrix3.identity())
                continue
            if Shader.Vector_3 == type_:
                self.send_vec_3(name_, Vector3(1, 1, 1))
                continue
            if Shader.Vector_2 == type_:
                self.send_vec_2(name_, Vector2(1, 1))
                continue
            if Shader.Float == type_:
                self.send_float(name_, 0.0)
                continue
            if Shader.Int == type_:
                self.send_int(name_, 0)
                continue

    def frag_shader(self, code: str, from_file: bool = True):
        if from_file:
            self.__frag_id = compileShader(self.__read_all_code(code), GL_FRAGMENT_SHADER)
            if self.__frag_id == 0:
                raise Exception(f"{GL_FRAGMENT_SHADER} shader compilation error...")
            self.__compile()
            return
        self.__frag_id = compileShader(code, GL_FRAGMENT_SHADER)
        if self.__frag_id == 0:
            raise Exception(f"{GL_FRAGMENT_SHADER} shader compilation error...")
        self.__compile()

    def vert_shader(self, code: str, from_file: bool = True):
        if from_file:
            self.__vert_id = compileShader(self.__read_all_code(code), GL_VERTEX_SHADER)
            if self.__vert_id == 0:
                raise Exception(f"{GL_VERTEX_SHADER} shader compilation error...")
            self.__compile()
            return
        self.__vert_id = compileShader(code, GL_VERTEX_SHADER)
        if self.__vert_id == 0:
            raise Exception(f"{GL_VERTEX_SHADER} shader compilation error...")
        self.__compile()

    def __compile(self):
        if self.__vert_id == 0:
            return
        if self.__frag_id == 0:
            return
        if self.__program_id != 0:
            self.delete_shader()
        self.__program_id = compileProgram(self.__vert_id, self.__frag_id)
        if self.__program_id == 0:
            raise Exception("Shader program compilation error...")
        Shader.__shader_instances[self.__program_id] = self
        self.bind()
        self.__get_all_attrib_locations()
        self.__get_all_uniform_locations()
        self.__get_all_uniform_blocks()
        print(self)

    def send_mat_3(self, mat_name: str, mat: Matrix3, transpose=GL_FALSE):
        loc = self.get_uniform_location(mat_name)
        if loc == -1:
            return
        self.bind()
        glUniformMatrix3fv(loc, 1, transpose, (GLfloat * 9)(*mat))

    def send_mat_4(self, mat_name: str, mat: Matrix4, transpose=GL_FALSE):
        loc = self.get_uniform_location(mat_name)
        if loc == -1:
            return
        self.bind()
        glUniformMatrix4fv(loc, 1, transpose, (GLfloat * 16)(*mat))

    def send_vec_2(self, vec_name: str, vec: Vector2):
        loc = self.get_uniform_location(vec_name)
        if loc == -1:
            return
        self.bind()
        glUniform2fv(loc, 1, (GLfloat * 2)(*vec))

    def send_vec_3(self, vec_name: str, vec: Vector3):
        loc = self.get_uniform_location(vec_name)
        if loc == -1:
            return
        self.bind()
        glUniform3fv(loc, 1, (GLfloat * 3)(*vec))

    def send_float(self, param_name: str, val: float):
        loc = self.get_uniform_location(param_name)
        if loc == -1:
            return
        self.bind()
        # print(param_name)
        glUniform1f(loc, GLfloat(val))

    def send_int(self, param_name: str, val: int):
        loc = self.get_uniform_location(param_name)
        if loc == -1:
            return
        self.bind()
        glUniform1i(loc, GLint(val))

    def bind(self):
        glUseProgram(self.__program_id)

    def unbind(self):
        glUseProgram(0)
