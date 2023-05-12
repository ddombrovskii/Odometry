from OpenGL.error import GLError
import functools


def gl_error_catch(_func):
    def gl_error_catch_decorator(func):
        @functools.wraps(func)
        def _gl_execute_and_catch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except GLError as _error:
                if _error.description is not None:
                    print(f"GLError: {_error.description.decode('ANSI')}")
                return None

            except RuntimeError as _error:
                if _error.args is not None:
                    print(f"RuntimeError: {_error.args}")
                return None

            except ValueError as _error:
                if _error.args is not None:
                    print(f"ValueError: {_error.args}")
                return None

            except Exception as _error:
                if _error.args is not None:
                    print(f"Exception: {_error.args}")
                return None
        return _gl_execute_and_catch
    return gl_error_catch_decorator(_func)
