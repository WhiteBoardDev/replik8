from src.page_handlers.tracker.annouce_request import AnnounceRequest
from src.page_handlers.tracker.peers import upsert_peer, get_peers
from src.page_handlers.tracker.bencoder import Bencoder
import dataclasses
from dataclasses import dataclass

_default_interval = 60

@dataclass
class AnnouceResponse():
    interval: int # seconds for downloader to wait until next annouce
    peers: list[dict[str, str | int]]

    def serialize(self) -> bytes:
        return Bencoder().withDict(dataclasses.asdict(self)).asBytes()

def response_to_annouce(annouce_request: AnnounceRequest) -> AnnouceResponse:
    """ Business Logic to handle the annouce request and return an annouce response.
    Delegate to other functional areas as needed.
    """
    upsert_peer(annouce_request) 
    peers = get_peers(annouce_request)
    return AnnouceResponse(_default_interval, peers)

