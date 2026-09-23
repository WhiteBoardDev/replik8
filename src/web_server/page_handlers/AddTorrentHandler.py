from tracker.TorrentFile import TorrentFile
from tracker.registry.torrent_registry import add_new_item
from tracker.bencoder import parse_bencoded_message
import web_server.templates.template_render as template_render
from dataclasses import dataclass
from io import BufferedIOBase
from typing import override, NamedTuple
from .PageHandlerAbs import PageHandlerAbs, RoutingConfig, MatchType, RequestAttrs, ResponseFuncs


_content_type_prefix='multipart/form-data; boundary='
_max_file_size=1_000_000

@dataclass
class BoundaryData:
    file_content: bytes
    headers: dict[str, str]


class ParsedBoundary(NamedTuple):
    boundary_data: BoundaryData
    next_boundary: bytes | None

def _handle_boundary(boundary: bytes, rfile: BufferedIOBase) -> ParsedBoundary:
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
            if line.startswith(boundary):
                next_boundary = line.strip()
                if next_boundary.endswith(b'--'):
                    next_boundary = None
                return ParsedBoundary(BoundaryData(bytes(file_content), headers), next_boundary)
            else:
                file_content.extend(line)
                if len(file_content) >= _max_file_size:
                    raise Exception("Max file size exceeded")
    raise Exception("malformed boundary data")


def _parse_form_request(rfile: BufferedIOBase) -> list[BoundaryData]:
        results = []
        current_boundary = rfile.__next__().strip()
        while current_boundary is not None:
            parsed = _handle_boundary(current_boundary, rfile)
            results.append(parsed.boundary_data)
            current_boundary = parsed.next_boundary

        return results

_content_disposition = "Content-Disposition"
def _find_boundary_with_form_input(field_name: str, boundaries: list[BoundaryData]) -> BoundaryData | None:
    for boundary in boundaries:
        if _content_disposition in boundary.headers and f"form-data; name=\"{field_name}\"" in boundary.headers[_content_disposition]:
            return boundary
    return None

class AddTorrentHandler(PageHandlerAbs):

    @override
    def get_routing_config(self):
        return RoutingConfig("/add-torrent", match_type=MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        res.wfile.write(template_render.render("add_torrent.html.jinja", {
        }))

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

        boundary_with_file = _find_boundary_with_form_input("file", form_data)
        assert boundary_with_file is not None


        content_disposition_parts = boundary_with_file.headers['Content-Disposition'].split(';')
        filename = [x.split('=')[-1] for x in content_disposition_parts if 'filename' in x][0].strip().replace("\"","")

        assert filename.endswith('.torrent')
        torrent_dict = parse_bencoded_message(boundary_with_file.file_content)


        boundary_with_registry_path = _find_boundary_with_form_input("registry_path", form_data)
        assert boundary_with_registry_path is not None

        torrent_file = TorrentFile(
            file_name=boundary_with_file.headers[_content_disposition].split('=')[-1].strip().replace('"', ''),
            file_contents=boundary_with_file.file_content
        )
        add_new_item(
            torrent_file=torrent_file, 
            user_id='TODO',
            description="TODO",
            path=boundary_with_registry_path.file_content.strip().decode()
            )

        content = b'go away. im not ready yet'
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.send_header("Content-Length", str(len(content)))
        res.end_headers()
        res.wfile.write(content)

        # TODO save torrent into registry

        