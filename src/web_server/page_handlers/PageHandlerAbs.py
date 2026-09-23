from enum import Enum
from io import BufferedIOBase
from dataclasses import dataclass
from typing import Callable, NamedTuple
from abc import abstractmethod
from abc import ABC


class MatchType(Enum):
    EXACT = 1
    STARTS_WITH = 2

@dataclass
class RoutingConfig:
    path: str 
    match_type: MatchType 

class Header(NamedTuple):
    key: str
    value: str

class ResponseFuncs:

    def __init__(self,
        send_response: Callable[[int], None],
        send_header: Callable[[str, str], None],
        end_headers: Callable[[], None],
        wfile: BufferedIOBase) -> None:
        self._send_response = send_response
        self._send_header = send_header
        self._end_headers = end_headers
        self.wfile = wfile
        self._outbound_headers: list[Header] = []
        self._headers_ended = False



    def send_response(self, status_code: int):
        self._response_code = status_code

    def send_header(self, key: str, value: str):
        header = Header(key,value)
        self._outbound_headers.append(header)

    def end_headers(self):
        """
        Flush status code and headers
        """
        assert self._headers_ended == False, "Already ended headers! Cannot call again"
        self._send_response(self._response_code)
        for header in self._outbound_headers:
            self._send_header(header.key, header.value)
        self._end_headers()
        self._headers_ended = True

@dataclass
class RequestAttrs:
    client_ip: str
    query_params: dict[str, list[str]]
    content_type: str | None
    rfile: BufferedIOBase
    full_path: str


class PageHandlerAbs(ABC):

    @abstractmethod
    def get_routing_config(self) -> RoutingConfig:
        pass

    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        raise NotImplementedError()
    def handle_post(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        raise NotImplementedError()