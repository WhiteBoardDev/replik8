from tracker.registry.internal.torrent_download import bencode_torrent_for_user
from tracker.users import get_user_by_id
import shared_utils.app_logging
from tracker.InvalidUserInputError import InvalidUserInputError
from typing import override
from web_server.page_handlers.PageHandlerAbs import PageHandlerAbs, RequestAttrs, ResponseFuncs, RoutingConfig, MatchType
import tracker.registry.torrent_registry as reg

def _get_info_hash(req: RequestAttrs):
    return req.query_params['info_hash'][0]


_logger = shared_utils.app_logging.get_logger("RegistryItemDownloadHandler")

class RegistryItemDownloadHandler(PageHandlerAbs):

    def __init__(self, announce_url: str) -> None:
        super().__init__()
        assert isinstance(announce_url, str)
        assert len(announce_url) > 0
        self._annouce_url = announce_url

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig(path="/api/torrent", match_type=MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        info_hash_hex = _get_info_hash(req) 
        info_hash = bytes.fromhex(info_hash_hex)

        assert req.authenticated_user_id is not None, "Internal error - this endpoint should be protected by auth"

        bencoded = bencode_torrent_for_user(req.authenticated_user_id, 
                                            info_hash,
                                            f"{self._annouce_url}/api/announce")
        if isinstance(bencoded, InvalidUserInputError):
            _logger.warning(bencoded.message)
            res.send_response(400)
            res.end_headers()
            res.wfile.write(b"Bad user input")
        else:
            res.send_response(200)
            res.send_header("Content-Length", str(len(bencoded[1])))
            res.send_header("Content-Disposition",f"attachment; filename={bencoded[0]}")
            res.send_header("Content-Type", "application/x-bittorrent")
            res.end_headers()
            res.wfile.write(bencoded[1])
