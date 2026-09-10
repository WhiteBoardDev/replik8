from src import template_render
from src.page_handlers.PageHandlerAbs import PageHandlerAbs, RoutingConfig, MatchType, RequestAttrs, ResponseFuncs
from typing import override

class IndexHandler(PageHandlerAbs):

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/", MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs,res: ResponseFuncs):
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        res.wfile.write(template_render.render("page_shell.html", {
            "site_name": "Replik8",
            "view" : "add_torrent.html"
        }))

