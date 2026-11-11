from web_server.page_handlers.RedeemInviteHandler import RedeemInviteHandler
from web_server.page_handlers.SignOutHandler import SignOutHandler
from web_server.page_handlers.UserManagementHandler import UserManagementHandler
from web_server.page_handlers.RegistryItemDownloadHandler import (
    RegistryItemDownloadHandler,
)
from .page_handlers.RegistryItemDetailHander import RegistryItemDetailHandler
from .page_handlers.RegistryTreeItemExpanded import RegistryTreeItemExpanded
from .page_handlers.RegistryTreeItemCollapsed import RegistryTreeItemCollapsed
from .page_handlers.AssetsHandler import AssetsHandler
from tracker.registry.user_management.users import root_user_check
from .page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from .page_handlers.IndexHandler import IndexHandler
from .page_handlers.PageHandlerAbs import (
    PageHandlerAbs,
    ResponseFuncs,
    RequestAttrs,
    MatchType,
)
from .page_handlers.BitTorrentTrackerHandler import BitTorrentTrackerHandler
from shared_utils.app_logging import get_logger
from .page_handlers import authentication_middleware
from .page_handlers.AddTorrentHandler import AddTorrentHandler
import argparse
import ssl
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import debugpy
import time

_logger = get_logger("root")
try:
    # Assumes the
    debugpy.connect(("127.0.0.1", 5678))
except Exception:
    _logger.warning("cannot connect to debugger")


_logger.info("Starting app")

arg_parser = argparse.ArgumentParser(prog="torrenttracker")

arg_parser.add_argument("--disable_https", default=False)
arg_parser.add_argument("--server_port", default=8080)
arg_parser.add_argument("--announce_url", required=True)
arg_parser.add_argument("--website_base_url", required=True)


args = arg_parser.parse_args()

assert isinstance(args.website_base_url, str)

_tracker_handler = BitTorrentTrackerHandler()
_redeem_invite_handler = RedeemInviteHandler()
_assets_handler = AssetsHandler()
_all_route_handlers: list[PageHandlerAbs] = [
    IndexHandler(),
    AddTorrentHandler(),
    RegistryTreeItemCollapsed(),
    RegistryTreeItemExpanded(),
    RegistryItemDetailHandler(),
    RegistryItemDownloadHandler(announce_url=args.announce_url),
    UserManagementHandler(args.website_base_url),
    SignOutHandler(),
    _redeem_invite_handler,
    _tracker_handler,
    _assets_handler,
]

not_found_handler = StatusCodeOnlyHandler(404)

_exact_route_paths = {
    handler.get_routing_config().path: handler
    for handler in _all_route_handlers
    if handler.get_routing_config().match_type.name == MatchType.EXACT.name
}
_starting_with_route_paths = [
    handler
    for handler in _all_route_handlers
    if handler.get_routing_config().match_type.name == MatchType.STARTS_WITH.name
]

_unauthenticated_paths = set(
    ["/favicon.ico", _redeem_invite_handler.get_routing_config().path]
)
_unauthenticated_path_prefix = set(
    [
        _assets_handler.get_routing_config().path,
        _tracker_handler.get_routing_config().path,
        "/.well-known",
    ]
)
root_user_check()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._do_verb("GET")

    def do_POST(self):
        self._do_verb("POST")

    def do_DELETE(self):
        self._do_verb("DELETE")

    def _do_verb(self, verb: str):
        responseFuncs = ResponseFuncs(
            self.send_response, self.send_header, self.end_headers, self.wfile
        )

        authenticated_user_id = None
        # Run all middleware

        if (
            len(
                [
                    x
                    for x in _unauthenticated_path_prefix
                    if self._get_path_only().startswith(x)
                ]
            )
            == 0
            and self._get_path_only() not in _unauthenticated_paths
        ):
            authenticated_user_id = authentication_middleware.handle(
                authentication_header=self.headers.get("Authorization"),
                cookie_header=self.headers.get("Cookie"),
                res=responseFuncs,
            )
            if authenticated_user_id is None:
                return

        # Then handle the request
        global _exact_route_paths
        global _starting_with_route_paths

        # Really basic handler routing, supporting `MatchType`
        handler = _exact_route_paths.get(self._get_path_only())
        if handler is None:
            for possible_handler in _starting_with_route_paths:
                if self._get_path_only().startswith(
                    possible_handler.get_routing_config().path
                ):
                    handler = possible_handler
                    break
        possible_content_length = self.headers.get("Content-Length")
        if possible_content_length is not None:
            possible_content_length = int(possible_content_length)

        reqAttrs = RequestAttrs(
            authenticated_user_id=authenticated_user_id,
            client_ip=self.client_address[0],
            query_params=self._get_query_params(),
            content_type=self.headers.get("Content-Type"),
            content_length=possible_content_length,
            rfile=self.rfile,
            full_path=self._get_path_only(),
        )
        if handler is None:
            not_found_handler.handle_get(reqAttrs, responseFuncs)
        else:
            if verb == "GET":
                handler.handle_get(reqAttrs, responseFuncs)
            elif verb == "POST":
                handler.handle_post(reqAttrs, responseFuncs)
            elif verb == "DELETE":
                handler.handle_delete(reqAttrs, responseFuncs)
            else:
                not_found_handler.handle_get(reqAttrs, responseFuncs)

    def _get_query_params(self):
        parsed_url = urlparse(self.path)
        # latin1 encoding important to propertly parse info_hash raw bytes on announce request
        query_parameters = parse_qs(parsed_url.query, encoding="latin1")
        return query_parameters

    def _get_path_only(self) -> str:
        return self.path.split("?")[0]


server_address_bind = ("localhost", args.server_port)
with HTTPServer(server_address_bind, SimpleHTTPRequestHandler) as httpd:
    if not args.disable_https:
        _logger.info("Running with HTTPS")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(".certs/cert.pem", ".certs/key.pem")
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    else:
        _logger.info("Running on HTTP plaintext")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        _logger.info("recieved shutdown signal")
    except Exception as e:
        _logger.info(e)

time.sleep(1)  # Give time to return http socket back to OS
_logger.info("Shut down server")
