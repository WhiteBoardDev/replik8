from shared_utils.app_logging import get_logger
from tracker.InvalidUserInputError import InvalidUserInputError
from tracker.annouce_request import AnnounceRequest
from tracker.datastore.connection import get_db
from dataclasses import dataclass
import dataclasses
from sqlite_utils.db import Table

from tracker.registry.torrent_registry import get_item_by_info_hash

_logger = get_logger("peers")

_query_seeders_leechers_count = """
SELECT 
count(CASE WHEN left = 0 THEN 1 END) as seeder_count,
count(CASE WHEN left > 0 THEN 1 END) as leecher_count
FROM peers
WHERE info_hash_v1 = ?
"""


# public module interface for peer
@dataclass
class Peer:
    ip: str
    port: str


# Internal database structure for peer
@dataclass
class PeerDatabaseRecord:
    info_hash_v1: bytes
    ip: str
    port: int
    user_id: str
    downloaded: int | None
    uploaded: int
    left: int


def _table_check():
    record = PeerDatabaseRecord(
        ip="foo",
        user_id="example",
        info_hash_v1=bytes([1, 1]),
        port=123,
        uploaded=100,
        downloaded=100,
        left=100,
    )

    table = _peers_table()
    table.upsert(
        dataclasses.asdict(record),
        pk=(
            "info_hash_v1",
            "user_id",
        ),
    )
    table.delete(
        (
            bytes([1, 1]),
            "example",
        )
    )


def _peers_table() -> Table:
    return get_db().table("peers")


def get_peers(annouce_request: AnnounceRequest) -> list[dict[str, str | int]]:
    """Fetches a list of peers for a given info_hash

    Excludes the accounce caller in the peer list.
    Asserts that the peer is allowed to download the torrent by
    checking against the user's registered IP addresses.

    In the case where the peer is not allowed, return an empty peer list.
    """

    # TODO IP check that the peer from the announce is on the allow list

    # TODO implement fetching N peers from the database
    return list()


@dataclass
class PeerStats:
    seeders: int
    leechers: int


def get_peer_stats(info_hash_v1: bytes) -> PeerStats | None:
    db = get_db()
    for row in db.query(_query_seeders_leechers_count, [info_hash_v1]):
        return PeerStats(seeders=row["seeder_count"], leechers=row["leecher_count"])
    return None


def _str_to_int_optional(input: str | None) -> int | None:
    if input is None:
        return None
    return int(input)


def upsert_peer(annouce_request: AnnounceRequest) -> InvalidUserInputError | None:
    """Given an annouce request, inserts the peer information into the system
    before adding as peer, check that the peer's IP address is on the allow list.
    If the peer is already tracked for the given info_hash, then upsert the peer's progress for
    tracking purposes.
    """
    # TODO implement ip check before saving

    registry_item = get_item_by_info_hash(annouce_request.info_hash)
    if isinstance(registry_item, InvalidUserInputError):
        _logger.warning("peer attempted to submit an unknown info_hash")
        return registry_item

    peer_record = PeerDatabaseRecord(
        info_hash_v1=annouce_request.info_hash,
        ip=annouce_request.ip,
        port=int(annouce_request.port),
        user_id=annouce_request.user_id,
        downloaded=_str_to_int_optional(annouce_request.downloaded),
        uploaded=int(annouce_request.uploaded),
        left=int(annouce_request.left),
    )

    peers_table = _peers_table()
    peers_table.upsert(
        dataclasses.asdict(peer_record),
        pk=(
            "info_hash_v1",
            "user_id",
        ),
    )
    return None


_table_check()
