from .form_parser_multipart import *
from tracker.registry.user_management.users import get_user_by_id
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
    def handle_put(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        """
        Updates the registry item detail
        upon success, returns the registry item detail
        upon failure, returns the same edit form with errors
        """
        form_data = parse_form_data(req)

        form_fields = ["id", "name", "registry-path", "description"]
        form_values = {
            x: get_field_value_as_str(x, form_data) or ""
            for x in form_fields
        }        
        info_hash_v1 = bytes.fromhex(form_values["id"])
        possible_error = reg.update_existing_item(info_hash_v1, form_values["name"], form_values["description"], form_values["registry-path"])
        if possible_error is not None:
            possible_error = possible_error.message
            
        self._render_info(info_hash_v1, form_values["id"], req, res, possible_error)
        


    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        info_hash_hex = _get_info_hash(req)
        if info_hash_hex is None:
            res.send_response(400)
            res.end_headers()
            res.wfile.write(b"Bad user input")
            return
        info_hash = bytes.fromhex(info_hash_hex)
        self._render_info(info_hash, info_hash_hex, req, res, None)



    def _render_info(self, info_hash: bytes, info_hash_hex: str, req: RequestAttrs, res: ResponseFuncs, edit_error_msg: str | None):
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

            view = "registry_item_detail.html.jinja" 
            if req.get_query_param("view") == "edit" or edit_error_msg is not None:
                view = "registry_item_detail_edit.html.jinja"
            
            res.wfile.write(
                template_render.render(
                    view,
                    {
                        "registry_item_detail": {
                            **registry_item.as_dict(),
                            "user_name": user_name,
                            "path_location": registry_item.path.split("/")[1:],
                            "path_location_raw": registry_item.path,
                            "delete_url": req.full_path + f"?info_hash={info_hash_hex}",
                            "info_hash_hex": info_hash_hex,
                            "download_url": f"/api/torrent?info_hash={info_hash_hex}",
                            "seeder_count": peer_stats.seeders,
                            "leecher_count": peer_stats.leechers,
                            "edit_url": f"/registry-item-detail?view=edit&info_hash={info_hash_hex}",
                        },
                        "edit_error_msg": edit_error_msg
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
