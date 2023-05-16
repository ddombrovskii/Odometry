from UIQt.GLUtilities.gl_shader import ShaderGL
from UIQt.GLUtilities.objects_pool import ObjectsPool
from Utilities.Geometry import Matrix4, Matrix3, Vector3, Vector2


class MaterialParam:

    def __init__(self, param_name, param_type):
        self._param_name = param_name
        self._param_type = param_type
        self._param_value = None
        self.shader_update = None
        if self.param_type not in ShaderGL.UniformTypes:
            return

        if ShaderGL.Matrix_4 == self.param_type:
            self._param_value = Matrix4.identity()
            self.shader_update = lambda shader: shader.send_mat_4(self.param_name, self._param_value)
            return

        if ShaderGL.Matrix_3 == self.param_type:
            self._param_value = Matrix3.identity()
            self.shader_update = lambda shader: shader.send_mat_3(self.param_name, self._param_value)
            return

        if ShaderGL.Vector_3 == self.param_type:
            self._param_value = Vector3(1, 1, 1)
            self.shader_update = lambda shader: shader.send_vec_3(self.param_name, self._param_value)
            return

        if ShaderGL.Vector_2 == self.param_type:
            self._param_value = Vector2(1, 1)
            self.shader_update = lambda shader: shader.send_vec_2(self.param_name, self._param_value)
            return

        if ShaderGL.Float == self.param_type:
            self._param_value = 0.0
            self.shader_update = lambda shader: shader.send_float(self.param_name, self._param_value)
            return

        if ShaderGL.Int == self.param_type:
            self._param_value = 0
            self.shader_update = lambda shader: shader.send_int(self.param_name, self._param_value)
            return
        raise ValueError(f"Incorrect material parameter type : {param_type} of parameter : {param_name}")

    @property
    def param_name(self) -> str:
        return self._param_name

    @property
    def param_type(self) -> int:
        return self._param_type

    @property
    def param_value(self):
        return self._param_value

    @param_value.setter
    def param_value(self, new_val):
        if not isinstance(new_val, type(self._param_value)):
            return
        self._param_value = new_val


class MaterialGL:

    materials = ObjectsPool()

    def __init__(self, shader: ShaderGL = None):
        # todo name
        self._bind_id = id(self)
        self._material_properties = {}
        self._shader: ShaderGL = shader

        for uniform in self._shader.uniforms.values():
            self._material_properties.update(
                {uniform.uniform_name: MaterialParam(uniform.uniform_name, uniform.data_type)})

        if shader.name.find("shader") != 0:
            self._name = shader.name.replace("shader", "material")
        else:
            self._name = f"{shader.name}_material"

        MaterialGL.materials.register_object(self)

    def __enter__(self):
        self.bind()

    def set_property_val(self, prop_name, prop_val) -> bool:
        if prop_name not in self._material_properties:
            return False
        prop = self._material_properties[prop_name]
        prop.param_value = prop_val
        with self._shader:
            prop.shader_update(self._shader)
        return True

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not MaterialGL.materials.check_if_name_valid(value):
            return
        MaterialGL.materials.unregister_object(self)
        self._name = value
        MaterialGL.materials.register_object(self)

    @property
    def shader(self) -> ShaderGL:
        return self._shader

    @property
    def bind_id(self) -> int:
        return self._bind_id

    def update_shader(self):
        with self._shader:
            self._update_shader()

    def _update_shader(self):
        pass

    def bind(self):
        if not MaterialGL.materials.bounded_update(self.bind_id):
            return
        self._shader.bind()
        self._update_shader()
