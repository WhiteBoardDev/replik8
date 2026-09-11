from page_handlers.tracker.registry_navigation import get_navigation_at_path
import template_render
from typing import override
from page_handlers.PageHandlerAbs import PageHandlerAbs, RequestAttrs, ResponseFuncs, RoutingConfig, MatchType


class RegistryTreeItemExpanded(PageHandlerAbs):

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig(
            path="/registry-tree-item-expanded",
            match_type=MatchType.EXACT
        )


    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:

        item_path = req.query_params['path'][0]
        nav_element = get_navigation_at_path(item_path) 
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()

        res.wfile.write(template_render.render(
            template_name="registry_tree_item_expanded.html.jinja",
            template_args=dict(
                {
                    "registry_tree_item": nav_element.as_dict()
                }
            )
        ))        
