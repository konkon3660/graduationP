# utils/suppress_alsa.py
import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_alsa_errors():
    fd = os.open(os.devnull, os.O_WRONLY)
    stderr_fd = sys.stderr.fileno()
    saved_stderr = os.dup(stderr_fd)
    os.dup2(fd, stderr_fd)
    try:
        yield
    finally:
        os.dup2(saved_stderr, stderr_fd)
        os.close(fd)
        os.close(saved_stderr)