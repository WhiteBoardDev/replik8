from tracker.InvalidUserInputError import InvalidUserInputError
from web_server.page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from tracker.registry.user_management.users import authenticate_user_by_peer_key
from tracker.annouce_response import response_to_annouce
from .PageHandlerAbs import (
    PageHandlerAbs,
    RoutingConfig,
    MatchType,
    ResponseFuncs,
    RequestAttrs,
)
from shared_utils.app_logging import get_logger
from typing import override
import dataclasses
from tracker import annouce_request


_logger = get_logger("BitTorrentTrackerHandler")

unauthenticated_resp = StatusCodeOnlyHandler(401)
invalid_input_resp = StatusCodeOnlyHandler(400)


class BitTorrentTrackerHandler(PageHandlerAbs):
    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/api/announce", MatchType.STARTS_WITH)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs):
        peer_key = req.full_path.split("/")[-1]

        user_id = authenticate_user_by_peer_key(peer_key)
        if user_id is None:
            unauthenticated_resp.handle_get(req, res)
        else:
            caller_annouce_request = annouce_request.parse(
                req.query_params, req.client_ip, user_id
            )
            log_context = dataclasses.asdict(caller_annouce_request)
            log_context["info_hash"] = log_context["info_hash"].hex()
            _logger.info("Incoming announce", extra={"context": log_context})
            response = response_to_annouce(caller_annouce_request)
            if isinstance(response, InvalidUserInputError):
                invalid_input_resp.handle_get(req, res)
            else:
                response_bytes = response.serialize()
                _logger.info(
                    "Annouce Response", extra={"context": {"resp": str(response_bytes)}}
                )
                res.send_response(200)
                res.send_header("Content-Type", "application/x-bittorrent")
                res.send_header("Content-Length", str(len(response_bytes)))
                res.end_headers()
                res.wfile.write(response_bytes)

    def handle_post(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        return super().handle_post(req, res)
