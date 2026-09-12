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
        """
        Handles a user uploading a .torrent file by:
        1. Parse the form-data POST from the browser and find the torrent file bytes
        2. Parse the bencoded torrent file into a readable dict of parts
        3. Use the contents of the "info" key in the torrent file to compute
        the total size of the torrent
        4. Parse the raw bencoded value for the "info" key. Perform a sha-1 on it.
        This sha-1 is called the "info_hash" and is the primary ID for the torrent
        5. Store the following information into the database


        Table: "torrent_registry"
        - "info_hash" - (bytes) - the primary key
        - "size" - (int) - size in bytes of the contents of the torrent
        - "name" - The user needs to specify a name for the torrent. This comes in
        from the form request and not from the file itself
        - "owner_user_id" - (str) - the user_id of who uploaded it. Stub this out for now to fake it.
        - "inserted_timestamp - (int) - unix epoch timestamp now() 


        After all that, the handler returns an HTML success page
        """

        assert req.content_type is not None and req.content_type.startswith(_content_type_prefix) == True
        form_data = _parse_form_request(req.rfile)
        # TODO parse torrent file and extra specific data
        content = b'go away. im not ready yet'
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.send_header("Content-Length", str(len(content)))
        res.end_headers()
        res.wfile.write(content)

        # TODO save torrent into registry

        