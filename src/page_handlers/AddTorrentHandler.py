from dataclasses import dataclass
import dataclasses
from src.datastore.connection import get_db

from io import BufferedIOBase
from typing import override
from sqlite_utils.db import Table
from .PageHandlerAbs import PageHandlerAbs, RoutingConfig, MatchType, RequestAttrs, ResponseFuncs


_content_type_prefix='multipart/form-data; boundary='
_max_file_size=1_000_000

@dataclass
class RegistryItem():

    """
    Display Name of the item in the registry. Could be a 
    """
    name: str

    """
    The parent navigation path in the registry where the item belongs
    """
    path: str

    """
    The info_hash of the torrent
    """
    info_hash: bytes

    """
    The owner of the registry item
    """
    owner_user_id: str

    def as_dict(self):
        return dataclasses.asdict(self)

def _get_table() -> Table:
    table = get_db().table('torrent_registry')
    return table

def insert_mock_data():
    """
    TODO ditch this when the add torrent feature is complete
    """
    table = _get_table()
    table.drop(ignore=True)


    mock_items = [
            RegistryItem("T1", "/one", info_hash=b'1', owner_user_id='123'),
            RegistryItem("T2", "/one", info_hash=b'2', owner_user_id='123'),
            RegistryItem("T3", "/one", info_hash=b'3', owner_user_id='123'),
            RegistryItem("T4", "/two", info_hash=b'4', owner_user_id='123'),
            RegistryItem("T5", "/two/one", info_hash=b'5', owner_user_id='123'),
            RegistryItem("T6", "/two/one", info_hash=b'6', owner_user_id='123'),
            RegistryItem("T7", "/two/one/one", info_hash=b'7', owner_user_id='123'),
            RegistryItem("T7", "/two/two/one", info_hash=b'8', owner_user_id='123'),
            RegistryItem("T7", "/two/two/two", info_hash=b'9', owner_user_id='123'),
            RegistryItem("T8", "/three", info_hash=b'10', owner_user_id='123'),
            RegistryItem("T9", "/three", info_hash=b'11', owner_user_id='123'),
            RegistryItem("T10", "/three/four", info_hash=b'12', owner_user_id='123'),
            RegistryItem("T11", "/three", info_hash=b'13', owner_user_id='123'),
            RegistryItem("T12", "/", info_hash=b'14', owner_user_id='123'),
        ]

    table.insert_all([x.as_dict() for x in mock_items], pk='info_hash') 

insert_mock_data()

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
        content = str(form_data)
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.send_header("Content-Length", str(len(content)))
        res.end_headers()
        res.wfile.write(content)
        # TODO parse torrent file and extra specific data

        # TODO save torrent into registry

        