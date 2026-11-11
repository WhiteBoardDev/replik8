from tracker.registry.registry_navigation import get_navigation_at_path
from web_server.page_handlers.common_ui_models.page_shell import page_shell_model
from web_server.templates import template_render
from web_server.page_handlers.PageHandlerAbs import (
    PageHandlerAbs,
    RoutingConfig,
    MatchType,
    RequestAttrs,
    ResponseFuncs,
)
from typing import override


class IndexHandler(PageHandlerAbs):
    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/", MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs):
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        root_item = get_navigation_at_path("/")
        res.wfile.write(
            template_render.render(
                "registry_tree.html.jinja",
                {
                    "page_shell": page_shell_model(req),
                    "registry_tree": root_item.as_dict(),
                },
            )
        )
