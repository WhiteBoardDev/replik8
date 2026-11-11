from web_server.page_handlers.PageHandlerAbs import RequestAttrs
from io import BufferedIOBase
from typing import NamedTuple

from dataclasses import dataclass


_content_type_prefix = "multipart/form-data; boundary="
_max_file_size = 1_000_000


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
            if line == b"\r\n":
                collecting_headers = False
                continue
            else:
                str_line = line.decode("utf-8")
                kv = str_line.index(":")
                header_key = str_line[:kv]
                header_value = str_line[kv + 1 :]
                headers[header_key] = header_value
        else:
            if line.startswith(boundary):
                next_boundary = line.strip()
                if next_boundary.endswith(b"--"):
                    next_boundary = None
                return ParsedBoundary(
                    BoundaryData(bytes(file_content), headers), next_boundary
                )
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


def find_boundary_with_form_input(
    field_name: str, boundaries: list[BoundaryData]
) -> BoundaryData | None:
    for boundary in boundaries:
        if (
            _content_disposition in boundary.headers
            and f'form-data; name="{field_name}"'
            in boundary.headers[_content_disposition]
        ):
            return boundary
    return None


def get_field_value_as_str(
    field_name: str, boundaries: list[BoundaryData]
) -> None | str:
    boundary = find_boundary_with_form_input(field_name, boundaries)
    if boundary is None:
        return None
    return boundary.file_content.decode()


def parse_form_data(req: RequestAttrs) -> list[BoundaryData]:
    assert (
        req.content_type is not None
        and req.content_type.startswith(_content_type_prefix) == True
    )
    form_data = _parse_form_request(req.rfile)
    return form_data
