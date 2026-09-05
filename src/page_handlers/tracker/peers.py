from datastore.connection import get_db
from page_handlers.tracker.annouce_request import AnnounceRequest


class Peer:
    ip: str
    port: str


def get_peers(annouce_request: AnnounceRequest) -> list[dict[str, str | int]]:
    """ Fetches a list of peers for a given info_hash
    
    Excludes the accounce caller in the peer list.
    Asserts that the peer is allowed to download the torrent by
    checking against the user's registered IP addresses.

    In the case where the peer is not allowed, return an empty peer list.
    """

    # TODO implement
    return list()

def upsert_peer(annouce_request: AnnounceRequest):
    """ Given an annouce request, inserts the peer information into the system
    before adding as peer, check that the peer's IP address is on the allow list.
    If the peer is already tracked for the given info_hash, then upsert the peer's progress for 
    tracking purposes.
    """
    db = get_db()
    db['peers']
    # TODO implement ip check
    # TODO implement peer IP persistence

