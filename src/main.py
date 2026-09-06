import argparse
from app_logging import get_logger
import ssl
from page_handlers.BitTorrentTrackerHandler import BitTorrentTrackerHandler
from urllib.parse import urlparse, parse_qs
from page_handlers.PageHandlerAbs import ResponseFuncs, RequestAttrs, MatchType
from page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from page_handlers.PageHandlerAbs import PageHandlerAbs
from page_handlers.IndexHandler import IndexHandler
from http.server import HTTPServer, BaseHTTPRequestHandler


_logger = get_logger('root')
_logger.info('Starting app')

arg_parser = argparse.ArgumentParser(
                    prog='torrenttracker')

arg_parser.add_argument("--disable_https", default=False)
arg_parser.add_argument("--server_port", default=8080)
args = arg_parser.parse_args()

_all_route_handlers: list[PageHandlerAbs] = [
    IndexHandler(),
    BitTorrentTrackerHandler()
]

not_found_handler = StatusCodeOnlyHandler(404)

_exact_route_paths = { handler.get_routing_config().path: handler for handler in _all_route_handlers if handler.get_routing_config().match_type == MatchType.EXACT}
_starting_with_route_paths = [handler for handler in _all_route_handlers if handler.get_routing_config().match_type == MatchType.STARTS_WITH]

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global _exact_route_paths 
        global _starting_with_route_paths

        # Really basic handler routing, supporting `MatchType`
        handler = _exact_route_paths.get(self._get_path_only())
        if handler is None:
            for possible_handler in _starting_with_route_paths:
                if self._get_path_only().startswith(possible_handler.get_routing_config().path):
                    handler = possible_handler
                    break

        responseFuncs = ResponseFuncs(
            self.send_response,
            self.send_header,
            self.end_headers,
            self.wfile
        )

        reqAttrs = RequestAttrs(self._get_query_params())
        if handler is None:
            not_found_handler.handle(reqAttrs,responseFuncs)
        else:
            handler.handle(reqAttrs, responseFuncs)

    def _get_query_params(self):
        parsed_url = urlparse(self.path)
        query_parameters = parse_qs(parsed_url.query)
        return query_parameters

    def _get_path_only(self) -> str:
        return self.path.split('?')[0]

server_address_bind = ('localhost', args.server_port)
httpd = HTTPServer(server_address_bind, SimpleHTTPRequestHandler)

if not args.disable_https:
    _logger.info("Running with HTTPS")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('.certs/cert.pem', '.certs/key.pem')
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
else:
    _logger.info("Running on HTTP plaintext")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.server_close()

_logger.info("Shut down server")