

from numbers import Number
from dataclasses import dataclass
from data_manager import is_safe_for_download
from io import BufferedIOBase


def handle():
    return None


_read_buffer_size = 1 # TODO increase this after testing

@dataclass
class DownloadState:
    written_bytes: Number

def _send_file(
    file_path: str,
    out_buffer: BufferedIOBase):
    if not is_safe_for_download(file_path):
       raise Exception('someone is trying to hack') 


    written_bytes = 0
    with open(file_path, mode='rb') as f:
        read_bytes = f.read(size=_read_buffer_size)
        f.write(read_bytes)
        written_bytes += len(read_bytes)

    return DownloadState(written_bytes)

