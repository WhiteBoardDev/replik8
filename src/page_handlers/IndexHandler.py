import template_render
from page_handlers.PageHandlerAbs import ResponseFuncs, RequestAttrs, RoutingConfig, MatchType
from page_handlers.PageHandlerAbs import PageHandlerAbs

class IndexHandler(PageHandlerAbs):

    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/", MatchType.EXACT)

    def handle(self, req: RequestAttrs,res: ResponseFuncs):
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        # TODO write nice homepage and render it
        # res.wfile.write(template_render.render("index.html", {
        #     "directory_list": data_manager.list_contents(None)
        # }))

