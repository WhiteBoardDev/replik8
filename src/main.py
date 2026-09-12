from page_handlers.RegistryItemDetailHander import RegistryItemDetailHandler
from page_handlers.RegistryTreeItemExpanded import RegistryTreeItemExpanded
from page_handlers.RegistryTreeItemCollapsed import RegistryTreeItemCollapsed
from src.page_handlers.AssetsHandler import AssetsHandler
from src.users import root_user_check
from src.page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from src.page_handlers.IndexHandler import IndexHandler
from src.page_handlers.PageHandlerAbs import PageHandlerAbs, ResponseFuncs, RequestAttrs, MatchType
from src.page_handlers.BitTorrentTrackerHandler import BitTorrentTrackerHandler
from src.app_logging import get_logger
from src.page_handlers import authentication_middleware
from src.page_handlers.AddTorrentHandler import AddTorrentHandler
import argparse
import ssl
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler


_logger = get_logger('root')
_logger.info('Starting app')

arg_parser = argparse.ArgumentParser(
                    prog='torrenttracker')

arg_parser.add_argument("--disable_https", default=False)
arg_parser.add_argument("--server_port", default=8080)
args = arg_parser.parse_args()

_tracker_handler = BitTorrentTrackerHandler()
_all_route_handlers: list[PageHandlerAbs] = [
    IndexHandler(),
    AddTorrentHandler(),
    AssetsHandler(),
    RegistryTreeItemCollapsed(),
    RegistryTreeItemExpanded(),
    RegistryItemDetailHandler(),
    _tracker_handler
]

not_found_handler = StatusCodeOnlyHandler(404)

_exact_route_paths = { handler.get_routing_config().path: handler for handler in _all_route_handlers if handler.get_routing_config().match_type.name == MatchType.EXACT.name}
_starting_with_route_paths = [handler for handler in _all_route_handlers if handler.get_routing_config().match_type.name == MatchType.STARTS_WITH.name]

_unauthenticated_routes = set([_tracker_handler.get_routing_config().path])

root_user_check()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self._do_verb("GET")

    def do_POST(self):
        self._do_verb("POST")

    def _do_verb(self, verb: str):
        responseFuncs = ResponseFuncs(
            self.send_response,
            self.send_header,
            self.end_headers,
            self.wfile
        )

        # Run all middleware
        if self._get_path_only() not in _unauthenticated_routes:
            authentication_middleware.handle(self.headers.get('Authorization'), responseFuncs)


        # Then handle the request 
        global _exact_route_paths 
        global _starting_with_route_paths

        # Really basic handler routing, supporting `MatchType`
        handler = _exact_route_paths.get(self._get_path_only())
        if handler is None:
            for possible_handler in _starting_with_route_paths:
                if self._get_path_only().startswith(possible_handler.get_routing_config().path):
                    handler = possible_handler
                    break


        reqAttrs = RequestAttrs(
            client_ip=self.client_address[0],
            query_params=self._get_query_params(),
            content_type=self.headers.get('Content-Type'),
            rfile=self.rfile,
            full_path=self._get_path_only())
        if handler is None:
            not_found_handler.handle_get(reqAttrs,responseFuncs)
        else:
            if verb == "GET":
                handler.handle_get(reqAttrs, responseFuncs)
            elif verb == "POST":
                handler.handle_post(reqAttrs, responseFuncs)
            else:
                not_found_handler.handle_get(reqAttrs,responseFuncs)

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