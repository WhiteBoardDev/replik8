from dataclasses import dataclass


def _first_param_or_none(key: str, params: dict[str, list[str]]) -> str | None:
    possible = params.get(key)
    if possible is None:
        return None
    return possible[0]

def _first_param_or_throw(key: str, params: dict[str, list[str]]) -> str:
    possible = params.get(key)
    if possible is None:
        raise Exception(f"{key} is required")
    return possible[0]
    

def parse(peer_key: str, query_params: dict[str, list[str]], client_id: str) -> AnnounceRequest:
    return AnnounceRequest(
        ip=_first_param_or_none('ip', query_params) or client_id,
        peer_key=peer_key,
        user_id="TODO - lookup via peer key",
        info_hash=_first_param_or_throw('info_hash', query_params),
        peer_id=_first_param_or_throw('peer_id', query_params),
        port=_first_param_or_throw('port', query_params),
        uploaded=_first_param_or_throw('uploaded', query_params),
        downloaded=_first_param_or_none('downlaoded', query_params),
        left=_first_param_or_throw('left', query_params),
        event=_first_param_or_none('event', query_params)
    )


@dataclass
class AnnounceRequest():
    ip: str
    peer_key: str
    user_id: str
    info_hash: str
    peer_id: str
    port: str 
    uploaded: str # base 10 ascii
    downloaded: str | None # base 10 ascii
    left: str # base 10 ascii
    event: str | None
