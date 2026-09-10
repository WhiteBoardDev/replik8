from dataclasses import dataclass
import dataclasses
from io import BufferedIOBase
from typing import override
from .PageHandlerAbs import PageHandlerAbs, RoutingConfig, MatchType, RequestAttrs, ResponseFuncs


_content_type_prefix='multipart/form-data; boundary='
_max_file_size=1_000_000

@dataclass
class BoundaryData:
    file_content: bytes
    headers: dict[str, str]

def _handle_boundary(boundary: bytes, rfile: BufferedIOBase) -> BoundaryData:
    collecting_headers = True
    headers = dict()
    file_content = bytearray() 
    for line in rfile:
        if collecting_headers:
            if line == b'\r\n':
                collecting_headers = False
                continue
            else:
                str_line = line.decode('utf-8')
                kv = str_line.index(':')
                header_key = str_line[:kv]
                header_value = str_line[kv+1:]
                headers[header_key] = header_value
        else:
            if b'--' + boundary + b'--\r\n' == line:
                return BoundaryData(bytes(file_content), headers)
            else:
                file_content.extend(line)
    raise Exception("malformed boundary data")


def _parse_form_request(rfile: BufferedIOBase) -> BoundaryData:
        for line in rfile:
            if line.startswith(b'--'):
                boundary = line[2:].strip()
                return _handle_boundary(boundary, rfile)
        raise Exception("improper formatted upload")


class AddTorrentHandler(PageHandlerAbs):

    @override
    def get_routing_config(self):
        return RoutingConfig("/add-torrent", match_type=MatchType.EXACT)


    @override
    def handle_post(self, req: RequestAttrs, res: ResponseFuncs):
        assert req.content_type is not None and req.content_type.startswith(_content_type_prefix) == True
        # TODO properly parse a form-data encoded request
        form_data = _parse_form_request(req.rfile)
        print('done?')
        # TODO parse torrent file and extra specific data

        # TODO save torrent into registry

        