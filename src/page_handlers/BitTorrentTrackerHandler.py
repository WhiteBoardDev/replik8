from src.page_handlers.tracker.annouce_response import response_to_annouce
from src.page_handlers.PageHandlerAbs import PageHandlerAbs, RoutingConfig, MatchType, ResponseFuncs, RequestAttrs
from src.app_logging import get_logger
from typing import override
import dataclasses
from .tracker import annouce_request


_logger = get_logger("BitTorrentTrackerHandler")

class BitTorrentTrackerHandler(PageHandlerAbs):

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/api/announce", MatchType.STARTS_WITH)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs):
        peer_key = self.get_routing_config().path.split('/')[-1]
        caller_annouce_request= annouce_request.parse(peer_key, req.query_params, req.client_ip)
        _logger.info("Incoming announce", extra={"context" :dataclasses.asdict(caller_annouce_request)})
        response = response_to_annouce(caller_annouce_request)
        response_bytes = response.serialize()
        _logger.info("Annouce Response", extra={ "context" : {"resp": str(response_bytes)}})
        res.send_response(200)
        res.send_header("Content-Type","application/x-bittorrent")
        res.send_header("Content-Length", str(len(response_bytes)))
        res.end_headers()
        res.wfile.write(response_bytes)

    def handle_post(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        return super().handle_post(req, res)

        
