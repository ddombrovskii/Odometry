class ObjectsPool:
    def __init__(self):
        self._bounded_id = -1
        self._objects_by_id = {}
        self._objects_by_name = {}

    @property
    def bounded_id(self) -> int:
        return self._bounded_id

    def bounded_update(self, bound_id: int) -> bool:
        if self._bounded_id == bound_id:
            return False
        self._bounded_id = bound_id
        return True

    def check_if_name_valid(self, name: str) -> bool:
        if name is None:
            return False
        if len(name) == 0:
            return False
        if name in self._objects_by_name:
            return False
        return True

    def register_object(self, _object) -> bool:
        flag = False
        if hasattr(_object, "bind_id"):
            if _object.bind_id <= 0:
                return flag
            self._objects_by_id.update({_object.bind_id: _object})
            flag |= True

        if hasattr(_object, "name"):
            self._objects_by_name.update({_object.name: _object})
            flag |= True

        return flag

    def unregister_object(self, _object) -> bool:
        flag = False
        if hasattr(_object, "bind_id"):
            if _object.bind_id in self._objects_by_id:
                del self._objects_by_id[_object.bind_id]
                flag |= True

        if hasattr(_object, "name"):
            if _object.name in self._objects_by_name:
                del self._objects_by_name[_object.name]
                flag |= True
        return flag

    def write_all_instances(self, file=None, prefix: str = "") -> None:
        print(f"\"{prefix}\":[\n", file=file, end="")
        print(',\n'.join(str(buffer) for buffer in self._objects_by_id.values()), file=file, end="")
        print(f"]\n", file=file, end="")

    def get_by_id(self, obj_id: int):
        return self._objects_by_id[obj_id] if obj_id in self._objects_by_id else None

    def get_by_name(self, obj_name: str):
        return self._objects_by_name[obj_name] if obj_name in self._objects_by_name else None

    def enumerate(self):
        for instance in self._objects_by_id.values():
            yield instance

    def delete_all(self):
        while len(self._objects_by_id) != 0:
            _, obj = self._objects_by_id.popitem()
            if hasattr(obj, "delete"):
                obj.delete()
        self._objects_by_id.clear()
        self._objects_by_name.clear()
