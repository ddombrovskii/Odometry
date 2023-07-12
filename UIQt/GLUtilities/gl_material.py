from Utilities.Geometry import Matrix4, Matrix3, Vector3, Vector2, Vector4
from .gl_objects_pool import ObjectsPoolGL
from .gl_texture import TextureGL
from .gl_shader import ShaderGL
from typing import Dict


class MaterialProperty:

    def __init__(self, prop_name: str, prop_type: int):
        self._prop_name = prop_name
        self._prop_type = prop_type
        self._prop_value = None
        self.shader_update = None

        if ShaderGL.Matrix_4 == self.prop_type:
            self._prop_value = Matrix4.identity()
            self.shader_update = lambda shader: shader.send_mat_4(self.prop_name, self._prop_value)
            return

        if ShaderGL.Matrix_3 == self.prop_type:
            self._prop_value = Matrix3.identity()
            self.shader_update = lambda shader: shader.send_mat_3(self.prop_name, self._prop_value)
            return

        if ShaderGL.Vector_3 == self.prop_type:
            self._prop_value = Vector3(1, 1, 1)
            self.shader_update = lambda shader: shader.send_vec_3(self.prop_name, self._prop_value)
            return

        if ShaderGL.Vector_2 == self.prop_type:
            self._prop_value = Vector2(1, 1)
            self.shader_update = lambda shader: shader.send_vec_2(self.prop_name, self._prop_value)
            return

        if ShaderGL.Float == self.prop_type:
            self._prop_value = 0.0
            self.shader_update = lambda shader: shader.send_float(self.prop_name, self._prop_value)
            return

        if ShaderGL.Int == self.prop_type:
            self._prop_value = 0
            self.shader_update = lambda shader: shader.send_int(self.prop_name, self._prop_value)
            return

        raise ValueError(f"Incorrect material parameter type : {prop_type} of parameter : {prop_type}")

    def __str__(self):
        try:
            return f"{{\n" \
                   f"\t\"name\" :\"{self.prop_name}\",\n" \
                   f"\t\"type\" :  {self.prop_type},\n" \
                   f"\t\"value\":  [{', '.join(str(v) for v in self.prop_value)}]\n" \
                   f"}}"
        except TypeError as er:
            return f"{{\n" \
                   f"\t\"name\" :\"{self.prop_name}\",\n" \
                   f"\t\"type\" :  {self.prop_type},\n" \
                   f"\t\"value\":  [{self.prop_value}]\n" \
                   f"}}"

    @property
    def prop_name(self) -> str:
        return self._prop_name

    @property
    def prop_type(self) -> int:
        return self._prop_type

    @property
    def prop_value(self):
        return self._prop_value

    @prop_value.setter
    def prop_value(self, new_val):
        if not isinstance(new_val, type(self._prop_value)):
            return
        self._prop_value = new_val


class MaterialGL:
    materials = ObjectsPoolGL()

    def __init__(self, shader: ShaderGL = None):
        # todo name
        self._bind_id = id(self)
        self._material_properties: Dict[str, MaterialProperty] = {}
        self._material_textures: Dict[int, TextureGL] = {}
        self._shader: ShaderGL | None = None
        if shader is None:
            self._name = f"material_{self.bind_id}"
            MaterialGL.materials.register_object(self)
            return

        self.shader = shader
        self._name = shader.name.replace("shader", "material") \
            if shader.name.find("shader") != 0 else f"{shader.name}_material"
        MaterialGL.materials.register_object(self)

    def __enter__(self):
        self.bind()

    def __str__(self):
        sep = ',\n'
        return f"{{\n" \
               f"\"name\": \"{self.name}\",\n" \
               f"\"shader\": \"{self.shader.name}\",\n" \
               f"\"params\": [\n{sep.join(str(v) for v in self.properties.values())}\n],\n" \
               f"\"textures\":[\n{sep.join(str(t)for t in self.textures.values())}]" \
               f"\n}}"

    @property
    def textures(self) -> Dict[int, TextureGL]:
        return self._material_textures

    @property
    def properties(self) -> Dict[str, MaterialProperty]:
        return self._material_properties

    def setting_from_json(self, material):
        if "name" in material:
            self.name = material["name"]

        if "shader" in material:
            self.shader = ShaderGL.shaders.get_by_name(material["shader"])

        if "properties" in material:
            for param in material["properties"]:
                if "name" not in param:
                    continue
                if "type" not in param:
                    continue
                if "args" not in param:
                    continue

                p_name = param["name"]

                if p_name not in self._material_properties:
                    continue
                try:
                    p_type = int(param["type"])
                    if p_type not in ShaderGL.UniformTypes:
                        continue
                except ValueError as _:
                    print(f"MaterialGL :: setting_from_json :: unknown param type {param['type']}")
                    continue

                try:
                    if p_type == ShaderGL.Float:
                        self._material_properties[p_name].prop_value = float(param["args"][0])
                        continue
                    if p_type == ShaderGL.Int:
                        self._material_properties[p_name].prop_value = int(param["args"][0])
                        continue
                    if p_type == ShaderGL.Vector_2:
                        self._material_properties[p_name].prop_value = \
                            Vector2(*(float(args) for args in param["args"]))
                        continue
                    if p_type == ShaderGL.Vector_3:
                        self._material_properties[p_name].prop_value = \
                            Vector3(*(float(args) for args in param["args"]))
                        continue
                    if p_type == ShaderGL.Vector_4:
                        self._material_properties[p_name].prop_value = \
                            Vector4(*(float(args) for args in param["args"]))
                        continue
                    if p_type == ShaderGL.Matrix_3:
                        self._material_properties[p_name].prop_value = \
                            Matrix3(*(float(args) for args in param["args"]))
                        continue
                    if p_type == ShaderGL.Matrix_4:
                        self._material_properties[p_name].prop_value = \
                            Matrix4(*(float(args) for args in param["args"]))
                        continue
                    if p_type == ShaderGL.Texture:
                        location = self._material_properties[p_name].prop_value = int(param["args"][0])
                        self._material_textures.update({location: TextureGL.textures.get_by_name(p_name)})
                        continue
                except ValueError as _:
                    print(f"MaterialGL :: setting_from_json :: args parsing error {param['args']}\n"
                          f"Default value for {p_type} will be assigned...")

        if "textures" in material:
            for texture in material["textures"]:
                if "name" not in texture:
                    continue
                if "type" not in texture:
                    continue
                if "location" not in texture:
                    continue

                p_name = texture["name"]

                try:
                    p_type = int(texture["type"])
                    if p_type not in ShaderGL.UniformTypes:
                        continue
                except ValueError as _:
                    print(f"MaterialGL :: setting_from_json :: unknown param type {texture['type']}")
                    continue
                try:
                    if p_type == ShaderGL.Texture:
                        location = int(texture["location"])
                        texture = TextureGL.textures.get_by_name(p_name)
                        if texture is None:
                            continue
                        self._material_textures.update({location: texture})
                        continue
                except ValueError as _:
                    print(f"MaterialGL :: setting_from_json :: args parsing error {texture['args']}\n"
                          f"Default value for {p_type} will be assigned...")

        self.update_shader()

    def set_property_val(self, prop_name, prop_val) -> bool:
        if prop_name not in self._material_properties:
            return False
        prop = self._material_properties[prop_name]
        prop.prop_value = prop_val
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

    @shader.setter
    def shader(self, shader: ShaderGL) -> None:
        if shader is None:
            return
        if self._shader is not None:
            if self._shader.name == shader.name:
                return
        self._shader = shader
        self._material_properties.clear()
        for uniform in self._shader.uniforms.values():
            if uniform.data_type == ShaderGL.Texture:
                continue
            if uniform.data_type == ShaderGL.TextureArray:
                continue
            if uniform.data_type == ShaderGL.TextureCube:
                continue
            self._material_properties.update(
                {uniform.uniform_name: MaterialProperty(uniform.uniform_name, uniform.data_type)})

    @property
    def bind_id(self) -> int:
        return self._bind_id

    def update_shader(self):
        with self._shader:
            self._update_shader()

    def _update_shader(self):
        for p in self.properties.values():
            p.shader_update(self._shader)
        for location, texture in self.textures.items():
            texture.bind_to_channel(location)

    def bind(self) -> bool:
        if not MaterialGL.materials.bounded_update(self.bind_id):
            return False
        self._shader.bind()
        self._update_shader()
        return True
