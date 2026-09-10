from pathlib import Path
from page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from web_assets import all_known_asset_paths
from page_handlers.PageHandlerAbs import PageHandlerAbs
from src.page_handlers.PageHandlerAbs import RequestAttrs, ResponseFuncs, RoutingConfig, MatchType

_not_found = StatusCodeOnlyHandler(404)

_mime_types_by_file_ext = {
    "js": "application/javascript",
    "css": "text/css"
}
class AssetsHandler(PageHandlerAbs):

    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig(
            path="/generated",
            match_type=MatchType.STARTS_WITH
        )

    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        file_path = req.full_path.removeprefix('/')
        if file_path in all_known_asset_paths:
            res.send_response(200)
            f_size = Path(file_path).stat().st_size
            res.send_header("Content-Length", str(f_size))
            res.send_header("Content-Type", _mime_types_by_file_ext[file_path.split(".")[-1]])
            res.send_header("Cache-Control", "max-age=604800")
            res.end_headers()
            with open(file_path, "rb") as f:
                res.wfile.write(f.read())
        else:
            _not_found.handle_get(req, res)