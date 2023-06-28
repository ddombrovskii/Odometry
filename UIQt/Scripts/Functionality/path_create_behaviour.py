import threading

from UIQt.Scripts.viewer_behaviour import ViewerBehaviour
from Utilities.Geometry import Vector3, Vector2, Transform
from UIQt.GLUtilities.gl_frame_buffer import FrameBufferGL
from PathFinder.path_finder import PathFinder
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_scene import SceneGL
from UIQt.point_widget import PointWidget
from UIQt.GLUtilities import gl_globals
from typing import List, Tuple


class PathCreateBehaviour(ViewerBehaviour):
    def __init__(self, scene_gl: SceneGL, map_directory: str, points_layout):
        super().__init__(scene_gl)
        self._path_request: bool = False
        self._points_layout = points_layout
        self._path_points_models: List[ModelGL] = []
        self._path_sections_models: List[ModelGL] = []
        self._path_sections: List[List[Vector2]] = []
        self._way_points_widgets = []
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
    def path_sections(self) -> List[List[Vector2]] :
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
        if len(_points) == 0:
            return None, None
        t = Transform()
        t.y = -50
        path = self.scene_gl.create_line(_points, transform=t.transform_matrix)
        return _points, path

    def _request_path(self, p1, p2):
        if self._path_request:
            return

        def crate_path(p1, p2):
            self._path_request = True
            points, path = self._create_path(p1, p2)

            if path is not None and len(points) >= 2:
                self._path_sections.append(points[1:])
                self._path_sections_models.append(path)
                self._populate_points_widgets(self._append_mode)
                self._path_request = False
                return

            self.scene_gl.remove_model(self._path_points_models[-1])
            del self._path_points_models[-1]
            if len(self._path_points_models) == 0:
                self.scene_gl.remove_model(self._path_points_models[0])
                del self._path_points_models[0]
            self._path_request = False

        thread = threading.Thread(target=crate_path, args=(p1, p2), daemon=True)

        thread.start()

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
                self._path_sections.append([Vector2(-y, -x)])
                self._append_mode += 1
                return

            if self._append_mode == 1:
                if (self._path_sections[-1][-1] - Vector2(-x, -y)).magnitude() < 0.1:
                    return
                point = self.scene_gl.create_box(mat_name="yellow_material")
                point.transform.origin = Vector3(-y, -50.0, -x)
                point.transform.scale = Vector3(0.1, 0.1, 0.1)
                self._path_points_models.append(point)
                points, path = self._create_path(self._path_points_models[-2], self._path_points_models[-1])

                if path is not None and len(points) >= 2:
                    self._path_sections.append(points[1:])
                    self._path_sections_models.append(path)
                    self._populate_points_widgets(self._append_mode)
                    return

                self.scene_gl.remove_model(self._path_points_models[-1])
                del self._path_points_models[-1]
                if len(self._path_points_models) == 0:
                    self.scene_gl.remove_model(self._path_points_models[0])
                    del self._path_points_models[0]

        if gl_globals.MOUSE_CONTROLLER.right_btn.is_pressed:
            self._append_mode += 1
            x, y = self._get_mouse_cords()
            point = self.scene_gl.create_box(mat_name="red_material")
            point.transform.origin = Vector3(-y, -50.0, -x)
            point.transform.scale = Vector3(0.1, 0.1, 0.1)
            self._path_points_models.append(point)
            self._request_path(self._path_points_models[-2], self._path_points_models[-1])
            # points, path = self._create_path(self._path_points_models[-2], self._path_points_models[-1])
            # if path is not None and len(points) >= 2:
            #     self._path_sections.append(points[1:])
            #     self._path_sections_models.append(path)
            #     self._populate_points_widgets(self._append_mode)
            #     self.enabled = False
            #     return
#
            # self.scene_gl.remove_model(self._path_points_models[-1])
            # del self._path_points_models[-1]
            # if len(self._path_points_models) == 0:
            #     self.scene_gl.remove_model(self._path_points_models[0])
            #     del self._path_points_models[0]

    def _append_point_view(self, pt_id: int, x: float, y: float, z: float):
        point = PointWidget(pt_id)
        point.setStyleSheet('background-color: #AAAAAA;')
        point.set_coordinates(x, y, z)
        self._points_layout.addWidget(point)
        return point

    def _clear_widgets(self):
        if len(self._way_points_widgets) != 0:
            for wp in self._way_points_widgets:
                for w in wp:
                    w.delete_clicked()

    def _populate_points_widgets(self, state):
        """
        state = 1 начало зелёное, остальные синие
        state = 2 все синие
        state = 3 конец синий, остальные синие
        """
        pts = self._path_sections[-1]
        widgets = [self._append_point_view(pt_id, pt.x, 0.0, pt.y) for pt_id, pt in enumerate(pts)]
        if state == 1:
            widgets[0].setStyleSheet('background-color: #00ff00;')
            widgets[-1].setStyleSheet('background-color: #ffff00;')
        if state == 2:
            widgets[0].setStyleSheet('background-color: #ffff00;')
            widgets[-1].setStyleSheet('background-color: #ffff00;')
        if state == 3:
            widgets[0].setStyleSheet('background-color: #ffff00;')
            widgets[-1].setStyleSheet('background-color: #ff0000;')

        self._way_points_widgets.append(widgets)
