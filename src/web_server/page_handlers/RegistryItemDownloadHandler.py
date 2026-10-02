import shared_utils.app_logging
from tracker.InvalidUserInputError import InvalidUserInputError
from typing import override
from web_server.page_handlers.PageHandlerAbs import PageHandlerAbs, RequestAttrs, ResponseFuncs
import tracker.registry.torrent_registry as reg

def _get_info_hash(req: RequestAttrs):
    return req.query_params['info_hash'][0]


_logger = shared_utils.app_logging.get_logger("RegistryItemDownloadHandler")

class RegistryItemDownloadHandler(PageHandlerAbs):

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        info_hash_hex = _get_info_hash(req) 
        info_hash = bytes.fromhex(info_hash_hex)

        registry_item = reg.get_by_info_hash(info_hash)
        if isinstance(registry_item, InvalidUserInputError):
            _logger.warning(registry_item.message)
            res.send_response(400)
            res.end_headers()
            res.wfile.write(b"Bad user input")
        else:

            
            res.send_response(200)
