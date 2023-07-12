from UIQt.CommonComponents.path_segment_widget import PathSegmentWidget
from UIQt.Scripts.viewer_behaviour import ViewerBehaviour
from Utilities.Geometry import Vector3, Vector2, Transform
from UIQt.GLUtilities.gl_frame_buffer import FrameBufferGL
from PathFinder.path_finder import PathFinder
from UIQt.GLUtilities import ModelGL
from UIQt.GLUtilities import SceneGL
from UIQt.GLUtilities import gl_globals
from typing import List, Tuple, Dict
from Utilities import RunningAverage


class PathCreateBehaviour(ViewerBehaviour):
    def __init__(self, scene_gl: SceneGL, map_directory: str, points_layout):
        super().__init__(scene_gl)
        self._path_request: bool = False
        self._points_layout = points_layout
        self._path_points_models: List[ModelGL] = []
        self._path_sections_models: List[ModelGL] = []
        self._path_sections: Dict[int, List[Vector2]] = {}
        self._sections_widgets = []
        self._append_mode = 0
        bounds = self.scene_gl.models_bounds
        size = bounds.size
        center = bounds.center
        self._path_finder: PathFinder = PathFinder(f"{map_directory}/Maps/weights_map.png",
                                                   size=Vector2(size.x, size.z),
                                                   origin=Vector2(center.x, center.z),
                                                   invert=False)

    @property
    def path_sections_models(self) -> List[ModelGL]:
        return self._path_sections_models

    @property
    def path_points_models(self) -> List[ModelGL]:
        return self._path_points_models

    @property
    def path_sections(self) -> List[List[Vector2]]:
        return self._path_sections

    @staticmethod
    def _get_mouse_cords() -> Tuple[float, float]:
        fb = FrameBufferGL.get_main_frame_buffer()
        x_pix, y_pix = gl_globals.MOUSE_CONTROLLER.left_btn.pressed_pos
        pos = gl_globals.MAIN_CAMERA.transform.origin
        x = 0.5 * (2.0 * x_pix / fb.width - 1.0) * gl_globals.MAIN_CAMERA.ortho_size + pos.z
        y = 0.5 * (2.0 * y_pix / fb.height - 1.0) * gl_globals.MAIN_CAMERA.ortho_size * \
            gl_globals.MAIN_CAMERA.aspect + pos.x
        return x, y

    def _on_enable(self):
        self._append_mode = 0

    def _create_path(self, p1: ModelGL, p2: ModelGL) -> Tuple[List[Vector2] | None, ModelGL | None]:
        if self._path_finder is None:
            return None, None
        _points = self._path_finder.search_path(Vector2(p1.transform.origin.x, p1.transform.origin.z),
                                                Vector2(p2.transform.origin.x, p2.transform.origin.z))
        if len(_points) < 2:
            return None, None

        delta_x = _points[0].x - p1.transform.origin.x
        delta_z = _points[0].y - p1.transform.origin.z

        if len(_points) == 0:
            return None, None
        t = Transform()
        t.x = -delta_x
        t.y = -50
        t.z = -delta_z
        path = self.scene_gl.create_line(_points, transform=t.transform_matrix)
        return _points, path

    # def _request_path(self, p1, p2):
    #     if self._path_request:
    #         return

    #     def crate_path(p1, p2):
    #         self._path_request = True
    #         points, path = self._create_path(p1, p2)

    #         if path is not None and len(points) >= 2:
    #             self._path_sections.append(points[1:])
    #             self._path_sections_models.append(path)
    #             self._populate_points_widgets(self._append_mode)
    #             self._path_request = False
    #             return

    #         self.scene_gl.remove_model(self._path_points_models[-1])
    #         del self._path_points_models[-1]
    #         if len(self._path_points_models) == 0:
    #             self.scene_gl.remove_model(self._path_points_models[0])
    #             del self._path_points_models[0]
    #         self._path_request = False

    #     thread = threading.Thread(target=crate_path, args=(p1, p2), daemon=True)

    #     thread.start()

    def _update(self):
        if gl_globals.MAIN_CAMERA.perspective_mode:
            return
        if self._path_request:
            return
        if gl_globals.MOUSE_CONTROLLER.left_btn.is_pressed:
            x, y = self._get_mouse_cords()

            if self._append_mode == 0:
                point = self.scene_gl.create_box(mat_name="green_material")
                point.transform.origin = Vector3(-y, -50.0, -x)
                point.transform.scale = Vector3(0.1, 0.1, 0.1)
                self._path_points_models.append(point)
                self._append_mode += 1
                return

            if self._append_mode == 1:
                # if (self._path_sections[-1][-1] - Vector2(-x, -y)).magnitude() < 0.1:
                #     return
                point = self.scene_gl.create_box(mat_name="yellow_material")
                point.transform.origin = Vector3(-y, -50.0, -x)
                point.transform.scale = Vector3(0.1, 0.1, 0.1)
                self._path_points_models.append(point)
                points, path = self._create_path(self._path_points_models[-2], self._path_points_models[-1])

                if path is not None and len(points) >= 2:
                    self._path_sections.update({id(points): points})
                    self._path_sections_models.append(path)
                    self._init_path_section_widget(id(points))
                    return

                self.scene_gl.remove_model(self._path_points_models[-1])
                del self._path_points_models[-1]
                if len(self._path_points_models) == 0:
                    self.scene_gl.remove_model(self._path_points_models[0])
                    del self._path_points_models[0]

        # if gl_globals.MOUSE_CONTROLLER.right_btn.is_pressed:
        #     self._append_mode += 1
        #     x, y = self._get_mouse_cords()
        #     point = self.scene_gl.create_box(mat_name="red_material")
        #     point.transform.origin = Vector3(-y, -50.0, -x)
        #     point.transform.scale = Vector3(0.1, 0.1, 0.1)
        #     self._path_points_models.append(point)
        #     self._request_path(self._path_points_models[-2], self._path_points_models[-1])

    def _init_path_section_widget(self, path_id):
        segment = PathSegmentWidget()
        points = self._path_sections[path_id]
        segment.start_pt  = Vector3(points[0].x,  0.0, points[0].y)
        segment.end_pt = Vector3(points[-1].x, 0.0, points[-1].y)
        total_lengths = sum((v1 - v2).magnitude() for v1, v2 in zip(points[:-1], points[1:]))
        segment.path_raw_length = total_lengths
        segment.path_length = total_lengths
        segment.path_name = f"Сегмент №{len(self._path_sections)}"
        segment.points_count = len(points)
        self._points_layout.addWidget(segment)

    def _on_decimate_change(self, value):
        decimate = (0, 2, 4, 8, 16)
        decimate_val = decimate[value]
        # self._rebuild_path(decimate_val)

    def _on_smooth_change(self, value):
        smooth = (0, 2, 4, 8, 16)
        ...

    def _rebuild_path(self, path_id, n_avg, n_dec):
        if n_dec == 0 and n_avg == 0:
            return
        x_smooth = RunningAverage(n_avg)
        y_smooth = RunningAverage(n_avg)
        path_points = self._path_sections[path_id]
        processed_points = []
        for i, v in enumerate(path_points):
            x = x_smooth(v.x)
            y = y_smooth(v.y)
            if i % n_dec != 0:
                continue
            processed_points.append(Vector2(x, y))
        last_point = path_points[-1]
        for i in range(n_avg):
            x = x_smooth(last_point.x)
            y = y_smooth(last_point.y)
            if (last_point.x - x) ** 2 + (last_point.y - y) ** 2 < 0.5:
                continue
            processed_points.append(Vector2(x, y))

        if last_point.x !=  processed_points[-1].x or last_point.y !=  processed_points[-1].y:
             processed_points.append(last_point)


