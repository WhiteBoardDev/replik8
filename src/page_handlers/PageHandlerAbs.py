from enum import Enum
from pathlib import Path
from io import BufferedIOBase
from dataclasses import dataclass
from typing import Callable
from abc import abstractmethod
from abc import ABC


class MatchType(Enum):
    EXACT = 1
    STARTS_WITH = 2

@dataclass
class RoutingConfig:
    path: str 
    match_type: MatchType 

@dataclass
class ResponseFuncs:
    send_response: Callable[[int], None]
    send_header: Callable[[str, str], None]
    end_headers: Callable[[], None]
    wfile: BufferedIOBase

@dataclass
class RequestAttrs:
    client_ip: str
    query_params: dict[str, list[str]]

class PageHandlerAbs(ABC):

    @abstractmethod
    def get_routing_config(self) -> RoutingConfig:
        pass


    @abstractmethod
    def handle(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        pass
