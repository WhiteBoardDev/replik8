from web_server.page_handlers.cookies import set_cookie
from typing import override
from web_server.page_handlers.PageHandlerAbs import (
    PageHandlerAbs,
    RequestAttrs,
    ResponseFuncs,
    RoutingConfig,
    MatchType,
)


_session_cookie_name = "rpl_sess"


class SignOutHandler(PageHandlerAbs):
    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/sign-out", match_type=MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        res.send_response(401)
        set_cookie(res, _session_cookie_name, "")
        res.end_headers()
        res.wfile.close()
