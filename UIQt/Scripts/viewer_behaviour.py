from UIQt.GLUtilities import SceneGL


class ViewerBehaviour:
    def __init__(self, scene_gl: SceneGL):
        self._scene_gl: SceneGL = scene_gl
        self._enabled = True
        self._start()

    def __del__(self):
        self._end()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if self.enabled == value:
            return
        self._enabled = value
        if self.enabled:
            self._on_enable()
        else:
            self._on_disable()

    @property
    def scene_gl(self) -> SceneGL:
        return self._scene_gl

    def update(self):
        if self.enabled:
            self._update()

    def reset(self):
        ...

    def _update(self):
        ...

    def _start(self):
        ...

    def _end(self):
        ...

    def _on_enable(self):
        ...

    def _on_disable(self):
        ...




