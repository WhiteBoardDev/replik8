from tracker.InvalidUserInputError import InvalidUserInputError
from tracker.annouce_request import AnnounceRequest
from tracker.peers import upsert_peer, get_peers
from tracker.bencoder import Bencoder
import dataclasses
from dataclasses import dataclass

_default_interval = 60


@dataclass
class AnnouceResponse:
    interval: int  # seconds for downloader to wait until next annouce
    peers: list[dict[str, str | int]]

    def serialize(self) -> bytes:
        return Bencoder().withDict(dataclasses.asdict(self)).asBytes()


def response_to_annouce(
    annouce_request: AnnounceRequest,
) -> AnnouceResponse | InvalidUserInputError:
    """Business Logic to handle the annouce request and return an annouce response.
    Delegate to other functional areas as needed.
    """
    possible_error = upsert_peer(annouce_request)
    if possible_error is not None:
        return possible_error
    peers = get_peers(annouce_request)
    return AnnouceResponse(_default_interval, peers)
