from Utilities.Geometry import Vector3, Vector2, Camera
from UIQt.GLUtilities import FrameBufferGL
from UIQt.GLUtilities import MaterialGL
from UIQt.GLUtilities import SceneGL


class TextureRenderer:
    def __init__(self, w: int, h: int, persistent_frame_buffer: bool = False):
        assert isinstance(w, int)
        assert isinstance(h, int)
        self._frame_buffer: FrameBufferGL = None
        self._override_material: MaterialGL = None
        self._camera: Camera = Camera()
        self._camera.aspect = w * 1.0 / h
        self._fb_persistent = persistent_frame_buffer
        self._init_frame_buffer(w, h)
        self._setup()

    def _setup(self):
        ...

    def _before_render(self, scene: SceneGL):
        ...

    def _after_render(self, scene: SceneGL):
        ...

    def __del__(self):
        if self._fb_persistent:
            return
        try:
            self._frame_buffer.delete()
        except Exception as _:
            ...

    def _init_frame_buffer(self, w: int, h: int):
        self._frame_buffer = FrameBufferGL(w, h)
        self._frame_buffer.name = f"_render_buffer_{id(self)}"
        self._frame_buffer.samples = 0
        self._frame_buffer.create_color_attachment_rgba_8("attachment_0")
        self._frame_buffer.create_depth()
        self._frame_buffer.validate()
        self._frame_buffer.clear_buffer()

    @property
    def frame_buffer(self) -> FrameBufferGL:
        return self._frame_buffer

    @property
    def override_material(self) -> MaterialGL:
        return self._override_material

    @override_material.setter
    def override_material(self, value: MaterialGL | None) -> None:
        if value is None:
            self._override_material = value
            return
        assert isinstance(value, MaterialGL)
        self._override_material = value

    @property
    def camera(self) -> Camera:
        return self._camera

    @property
    def width(self) -> int:
        return self._frame_buffer.width

    @property
    def height(self) -> int:
        return self._frame_buffer.height

    @width.setter
    def width(self, value: int) -> None:
        assert isinstance(value, int)
        assert value > 0
        if value == self._frame_buffer.width:
            return
        h = self._frame_buffer.height
        self._frame_buffer.delete()
        self._init_frame_buffer(value, h)
        self._camera.aspect = value * 1.0 / h

    @height.setter
    def height(self, value: int) -> None:
        assert isinstance(value, int)
        assert value > 0
        if value == self._frame_buffer.height:
            return
        w = self._frame_buffer.width
        self._frame_buffer.delete()
        self._init_frame_buffer(w, value)
        self._camera.aspect = w * 1.0 / value

    def render(self, scene: SceneGL):
        scene.override_material = self.override_material
        self._before_render(scene)
        scene.draw_scene(self._frame_buffer, self._camera)
        self._after_render(scene)
        return self._frame_buffer.grab_snap_shot("attachment_0")

    def render_to_image(self, scene: SceneGL, image_file_path: str):
        self.render(scene).save(image_file_path)


class WeightsMapRenderer(TextureRenderer):
    def __init__(self, w: int = 1024, h: int = 1024, persistent_frame_buffer: bool = False):
        super().__init__(w, h, persistent_frame_buffer)

    def _setup(self):
        self.frame_buffer.name = "map_weights_render_buffer"
        self._camera.perspective_mode = False
        self.override_material = MaterialGL.materials.get_by_name("map_material")

    def _before_render(self, scene: SceneGL):
        bbox = scene.models_bounds
        sx, sy, sz = bbox.size
        x, y, z = bbox.center
        self._camera.ortho_size = max(sx, sz)
        self._camera.look_at(Vector3(-x, 0, -z), Vector3(0, 1.5 * sy, 0) + Vector3(-x, 0, -z), Vector3(-1, 0, 0))
        if self.override_material is not None:
            self.override_material.set_property_val("min_bound", bbox.min)
            self.override_material.set_property_val("max_bound", bbox.max)
        scene.draw_gizmos = False

    def _after_render(self, scene: SceneGL):
        scene.draw_gizmos = True
        scene.override_material = None


class ScenePreviewsRenderer(TextureRenderer):
    def __init__(self, w: int = 256, h: int = 256, persistent_frame_buffer: bool = False):
        super().__init__(w, h, persistent_frame_buffer)

    def _setup(self):
        self.frame_buffer.name = "scene_previews_render_buffer"

    def _before_render(self, scene: SceneGL):
        scene.draw_gizmos = False

    def _after_render(self, scene: SceneGL):
        scene.draw_gizmos = True


class SceneViewRenderer:
    def __init__(self, scene: SceneGL, w: int = 512, h: int = 512):
        self._renderer: ScenePreviewsRenderer = ScenePreviewsRenderer(w, h)
        self._heights_fb: FrameBufferGL = FrameBufferGL.frame_buffers.get_by_name("map_weights_render_buffer")
        self._scene = scene

    def get_height(self, x: float, y: float) -> float:
        if self._heights_fb is None:
            return 0.0
        _size: Vector3   = self._scene.models_bounds.size
        _origin: Vector3 = self._scene.models_bounds.center
        row = int(self._heights_fb.height * (x - _origin.x) / _size.x)
        col = int(self._heights_fb.width  * (y - _origin.z) / _size.z)
        return self._heights_fb.read_pixel(row, col)

    def render(self, target: Vector2, eye: Vector2):
        _target = Vector3(target.x, self.get_height(*target), target.z)
        _eye = Vector3(eye.x, self.get_height(*eye), eye.z)
        self._renderer.camera.look_at(_target, _eye)
        return self._renderer.render(self._scene)

    def render_to_file(self, target: Vector2, eye: Vector2, file_path: str):
        self.render(target, eye).save(file_path)






