from page_handlers.tracker.registry_navigation import get_navigation_at_path
from src.web_assets import css_assets, js_assets
from src import template_render
from src.page_handlers.PageHandlerAbs import PageHandlerAbs, RoutingConfig, MatchType, RequestAttrs, ResponseFuncs
from typing import override


def page_shell_model():
    return {
        "link_includes": [{"src": x.local_destination(), "integrity":x.integrity_hash} for x in css_assets],
        "script_includes": [{"src": x.local_destination(), "integrity": x.integrity_hash} for x in js_assets],
        "site_name": "Replik8",
        "view" : "registry_tree.html.jinja"
    }


class IndexHandler(PageHandlerAbs):

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/", MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs,res: ResponseFuncs):
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        root_item = get_navigation_at_path('/') 
        res.wfile.write(template_render.render("page_shell.html.jinja", {
            "page_shell": page_shell_model(),
            "registry_tree": root_item.as_dict()
        }))

