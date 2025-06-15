import ctypes
import contextlib

@contextlib.contextmanager
def suppress_alsa_errors():
    """ALSA C 레벨 에러 출력을 억제하는 핸들러."""
    try:
        asound = ctypes.cdll.LoadLibrary("libasound.so")
        ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
            None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p
        )
        def py_error_handler(filename, line, function, err, fmt):
            pass  # 무시
        c_handler = ERROR_HANDLER_FUNC(py_error_handler)
        asound.snd_lib_error_set_handler(c_handler)
        yield
    finally:
        asound.snd_lib_error_set_handler(None)
