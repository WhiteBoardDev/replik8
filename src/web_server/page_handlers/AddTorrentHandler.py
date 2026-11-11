from .form_parser_multipart import (
    parse_form_data,
    find_boundary_with_form_input,
    get_field_value_as_str,
)
from tracker.InvalidUserInputError import InvalidUserInputError
from tracker.TorrentFile import TorrentFile
from tracker.registry.torrent_registry import add_new_item, get_by_info_hash
from web_server.page_handlers.common_ui_models.page_shell import page_shell_model
import web_server.templates.template_render as template_render
from typing import override
from .PageHandlerAbs import (
    PageHandlerAbs,
    RoutingConfig,
    MatchType,
    RequestAttrs,
    ResponseFuncs,
)

_content_disposition = "Content-Disposition"


class AddTorrentHandler(PageHandlerAbs):
    @override
    def get_routing_config(self):
        return RoutingConfig("/add-torrent", match_type=MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        self._send_add_torrent_page(req, res, None)

    def _send_add_torrent_page(
        self, req: RequestAttrs, res: ResponseFuncs, error: str | None
    ):
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        res.wfile.write(
            template_render.render(
                "add_torrent.html.jinja",
                {"error": error, "page_shell": page_shell_model(req)},
            )
        )

    @override
    def handle_post(self, req: RequestAttrs, res: ResponseFuncs):
        """
        Handles a user uploading a .torrent file by:
        1. Parse the form-data POST from the browser and find the torrent file bytes
        2. Parse the bencoded torrent file into a readable dict of parts
        3. Use the contents of the "info" key in the torrent file to compute
        the total size of the torrent
        4. Parse the raw bencoded value for the "info" key. Perform a sha-1 on it.
        This sha-1 is called the "info_hash" and is the primary ID for the torrent
        5. Store the following information into the database


        Table: "torrent_registry"
        - "info_hash" - (bytes) - the primary key
        - "size" - (int) - size in bytes of the contents of the torrent
        - "name" - The user needs to specify a name for the torrent. This comes in
        from the form request and not from the file itself
        - "owner_user_id" - (str) - the user_id of who uploaded it. Stub this out for now to fake it.
        - "inserted_timestamp - (int) - unix epoch timestamp now()


        After all that, the handler returns an HTML success page
        """
        form_data = parse_form_data(req)

        boundary_with_file = find_boundary_with_form_input("file", form_data)
        if boundary_with_file is None:
            self._send_add_torrent_page(
                req, res, "Must select valid torrent file to upload"
            )
        else:
            content_disposition_parts = boundary_with_file.headers[
                "Content-Disposition"
            ].split(";")
            filename = (
                [
                    x.split("=")[-1]
                    for x in content_disposition_parts
                    if "filename" in x
                ][0]
                .strip()
                .replace('"', "")
            )

            assert filename.endswith(".torrent")
            boundary_with_registry_path = find_boundary_with_form_input(
                "registry_path", form_data
            )
            assert boundary_with_registry_path is not None

            torrent_file = TorrentFile(
                file_name=boundary_with_file.headers[_content_disposition]
                .split("=")[-1]
                .strip()
                .replace('"', ""),
                file_contents=boundary_with_file.file_content,
            )

            assert req.authenticated_user_id is not None
            info_hash = add_new_item(
                torrent_file=torrent_file,
                user_id=req.authenticated_user_id,
                description=get_field_value_as_str("description", form_data) or "",
                path=boundary_with_registry_path.file_content.strip().decode(),
            )
            if isinstance(info_hash, InvalidUserInputError):
                self._send_add_torrent_page(req, res, info_hash.message)
            else:
                res.send_response(200)
                res.send_header("Content-Type", "text/html")
                res.end_headers()
                res.wfile.write(
                    template_render.render(
                        "add_torrent_success.html.jinja",
                        {
                            "target": f"/registry-item-detail?info_hash={info_hash.hex()}",
                            "page_shell": page_shell_model(req),
                        },
                    )
                )
