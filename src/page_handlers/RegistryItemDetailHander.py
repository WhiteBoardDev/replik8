import template_render
from typing import override
from page_handlers.PageHandlerAbs import PageHandlerAbs, RequestAttrs, ResponseFuncs, RoutingConfig, MatchType


class RegistryItemDetailHandler(PageHandlerAbs):

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig(
            path="/registry-item-detail",
            match_type=MatchType.EXACT
        )


    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        res.wfile.write(template_render.render("registry_item_detail.html.jinja", {
            
        }))

