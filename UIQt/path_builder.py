from Utilities.Geometry import Vector2, Vector3
from UIQt.GLUtilities.gl_model import ModelGL
from UIQt.GLUtilities.gl_scene import SceneGL
from UIQt.point_widget import PointWidget
from typing import Dict, Tuple, List


class PathBuilder:
    def __init__(self, scene: SceneGL):
        self._free_keys = []
        self._paths_models: Dict[int, Tuple[ModelGL, ModelGL, ModelGL]] = {}
        self._paths_points: Dict[int, List[Vector2]] = {}
        self._path_points_widgets: Dict[int, List[PointWidget]] = {}
        self._paths_widgets: Dict[int, List[Vector2]] = {}
        self._gl_scene: SceneGL = scene

    def _append_point_view(self, parent, pt_id: int, x: float, y: float, z: float):
        point = PointWidget(pt_id)
        point.setStyleSheet('background-color: #AAAAAA;')
        point.set_coordinates(x, y, z)
        parent.addWidget(point)
        return point

    def _populate_points_widgets(self, parent, points):
        _way_points_widgets = [self._append_point_view(parent, pt_id, pt.x, 0.0, pt.y)
                                    for pt_id, pt in enumerate(points)]
        _way_points_widgets[0].setStyleSheet('background-color: #00ff00;')
        _way_points_widgets[-1].setStyleSheet('background-color: #ff0000;')
        return _way_points_widgets

    def append_path(self, points: List[Vector2]):
        key = len(self._paths_models) if len(self._free_keys) == 0 else self._free_keys.pop()
        start = self._gl_scene.create_box(mat_name="green_material")
        start.transform.origin = Vector3(points[0].x, 0.0, points[0].y)
        start.transform.scale  = Vector3(0.1, 0.0, 0.1)

        finish = self._gl_scene.create_box(mat_name="red_material")
        finish.transform.origin = Vector3(points[-1].x, 0.0, points[-1].y)
        finish.transform.scale  = Vector3(0.1, 0.0, 0.1)

        path = self._gl_scene.create_line(points)
        self._paths_models.update({key: (start, finish, path)})
        self._paths_points.update({key: points})

    def contains_path_id(self, path_id: int):
        return path_id in self._paths_models

    def delete_point(self, path_id: int, point_id: int):
        if not self.contains_path_id(path_id):
            return

        points = self._paths_points[path_id]

        if point_id < 0:
            return

        if point_id >= len(points):
            return

        if len(points) - 1 == 1:
            self.delete_by_index(path_id)
            return

        start_model, end_model, points_model = self._paths_models[path_id]
        points_widgets = self._path_points_widgets[path_id]
        points_widgets[point_id].delete_clicked()
        del points_widgets[point_id]
        del points[point_id]
        end_model.transform.origin = Vector3(points[point_id].x, 0.0, points[point_id].y)
        self._gl_scene.remove_model(points_model)
        points_model = self._gl_scene.create_line(points)

        if point_id == 0:
            start_model.transform.origin = Vector3(points[0].x, 0.0, points[0].y)
            return

        if point_id == len(points) - 1:
            end_model.transform.origin = Vector3(points[-1].x, 0.0, points[-1].y)

        self._paths_models[path_id] = (start_model, end_model, points_model)

    def delete_by_index(self, index):
        if not self.contains_path_id(index):
            return
        self._free_keys.append(index)
        start, end, path = self._paths_models[index]
        self._gl_scene.remove_model(start)
        self._gl_scene.remove_model(end)
        self._gl_scene.remove_model(path)
        del self._paths_points[index]

        widgets = self._path_points_widgets[index]
        for w in widgets:
            w.delete_clicked()
        del self._path_points_widgets[index]

        widget = self._paths_widgets[index]
        # widget.delete_later()
        del self._paths_widgets[index]

    def delete_all(self):
        for index in self._paths_models.keys():
            self.delete_by_index(index)

    def show(self):
        for start, end, path in self._paths_models.values():
            start.enable = True
            end.enable = True
            path.enable = True

    def hide(self):
        for start, end, path in self._paths_models.values():
            start.enable = False
            end.enable = False
            path.enable = False
