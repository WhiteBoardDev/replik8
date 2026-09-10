from src.page_handlers.tracker.annouce_request import AnnounceRequest
from src.datastore.connection import get_db
from dataclasses import dataclass
import dataclasses
from sqlite_utils.db import Table


# public module interface for peer
@dataclass
class Peer:
    ip: str
    port: str

# Internal database structure for peer
@dataclass
class PeerDatabaseRecord:
    info_hash: bytes
    ip: str
    port: int
    user_id: str
    downloaded: int | None
    uploaded: int
    left: int

def _peers_table() -> Table:
    table = get_db()['peers']
    if isinstance(table, Table):
        return table
    raise Exception("peers isn't supposed to be a view")

def get_peers(annouce_request: AnnounceRequest) -> list[dict[str, str | int]]:
    """ Fetches a list of peers for a given info_hash
    
    Excludes the accounce caller in the peer list.
    Asserts that the peer is allowed to download the torrent by
    checking against the user's registered IP addresses.

    In the case where the peer is not allowed, return an empty peer list.
    """

    # TODO implement fetching N peers from the database
    return list()

def _str_to_int_optional(input: str | None) -> int | None:
    if input is None:
        return None
    return int(input)

def upsert_peer(annouce_request: AnnounceRequest):
    """ Given an annouce request, inserts the peer information into the system
    before adding as peer, check that the peer's IP address is on the allow list.
    If the peer is already tracked for the given info_hash, then upsert the peer's progress for 
    tracking purposes.
    """
    # TODO implement ip check before saving

    peer_record = PeerDatabaseRecord(
        info_hash=annouce_request.info_hash.encode("utf-8"),
        ip = annouce_request.ip or "TODO",
        port=int(annouce_request.port),
        user_id=annouce_request.user_id,
        downloaded=_str_to_int_optional(annouce_request.downloaded),
        uploaded=int(annouce_request.uploaded),
        left=int(annouce_request.left)
    )

    peers_table = _peers_table()
    peers_table.upsert(dataclasses.asdict(peer_record), pk=("info_hash","user_id",))

