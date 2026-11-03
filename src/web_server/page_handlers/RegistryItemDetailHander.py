from tracker.users import get_user_by_id
from tracker.peers import get_peer_stats, PeerStats
import shared_utils.app_logging
from tracker.InvalidUserInputError import InvalidUserInputError
import web_server.templates.template_render as template_render
import tracker.registry.torrent_registry as reg
from typing import override
from .PageHandlerAbs import (
    PageHandlerAbs,
    RequestAttrs,
    ResponseFuncs,
    RoutingConfig,
    MatchType,
)

_logger = shared_utils.app_logging.get_logger("RegistryItemDetailHandler")


def _get_info_hash(req: RequestAttrs) -> str | None:
    if "info_hash" in req.query_params:
        possible = req.query_params["info_hash"][0]
        if isinstance(possible, str):
            return possible
    return None


class RegistryItemDetailHandler(PageHandlerAbs):
    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig(path="/registry-item-detail", match_type=MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        info_hash_hex = _get_info_hash(req)
        if info_hash_hex is None:
            res.send_response(400)
            res.end_headers()
            res.wfile.write(b"Bad user input")
            return

        info_hash = bytes.fromhex(info_hash_hex)
        registry_item = reg.get_by_info_hash(info_hash)
        peer_stats = get_peer_stats(info_hash)
        if peer_stats is None:
            _logger.error(f"Unable to resolve peer stats for info hash {info_hash_hex}")
            peer_stats = PeerStats(-1, -1)
        if isinstance(registry_item, InvalidUserInputError):
            _logger.warning(registry_item.message)
            res.send_response(400)
            res.end_headers()
            res.wfile.write(b"Bad user input")
        else:
            user_name = get_user_by_id(registry_item.owner_user_id)
            if user_name is None:
                user_name = ""
            else:
                user_name = user_name.name

            res.send_response(200)
            res.send_header("Content-Type", "text/html")
            res.end_headers()
            res.wfile.write(
                template_render.render(
                    "registry_item_detail.html.jinja",
                    {
                        "registry_item_detail": {
                            **registry_item.as_dict(),
                            "user_name": user_name,
                            "path_location": registry_item.path.split("/")[1:],
                            "delete_url": req.full_path + f"?info_hash={info_hash_hex}",
                            "download_url": f"/api/torrent?info_hash={info_hash_hex}",
                            "seeder_count": peer_stats.seeders,
                            "leecher_count": peer_stats.leechers,
                        }
                    },
                )
            )

    @override
    def handle_delete(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        info_hash_hex = _get_info_hash(req)
        if info_hash_hex is None:
            res.send_response(400)
            res.end_headers()
            res.wfile.write(b"Bad user input")
            return

        info_hash = bytes.fromhex(info_hash_hex)
        assert req.authenticated_user_id is not None
        delete_result = reg.delete_item(req.authenticated_user_id, info_hash)

        if isinstance(delete_result, InvalidUserInputError):
            res.send_response(400)
            res.end_headers()
            res.wfile.write(delete_result.message.encode())
        else:
            res.send_response(200)
            res.send_header("Content-Type", "text/html")
            res.end_headers()
            res.wfile.write("</nbsp>".encode())
