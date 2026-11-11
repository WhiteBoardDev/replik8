from tracker.InvalidUserInputError import InvalidUserInputError
from web_server.page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from tracker.registry.user_management.invites import generate_invite
from typing_extensions import override
from web_server.page_handlers.PageHandlerAbs import (
    PageHandlerAbs,
    RequestAttrs,
    ResponseFuncs,
    RoutingConfig,
    MatchType,
)
from web_server.page_handlers.common_ui_models.page_shell import page_shell_model
from web_server.templates import template_render


unauth = StatusCodeOnlyHandler(401)


class UserManagementHandler(PageHandlerAbs):
    def __init__(self, website_base_url: str):
        self.website_base_url = website_base_url

    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig(path="/user-management", match_type=MatchType.EXACT)

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        res.wfile.write(
            template_render.render(
                "user_management.html.jinja",
                {
                    "invites_remaining": 0,
                    "page_shell": page_shell_model(req),
                    "invite_url": self.get_routing_config().path,
                },
            )
        )

    @override
    def handle_post(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        if req.authenticated_user_id is None:
            unauth.handle_get(req, res)
        else:
            invite_pairs = generate_invite(req.authenticated_user_id)
            error_message = None
            if isinstance(invite_pairs, InvalidUserInputError):
                error_message = invite_pairs.message
                invite_pairs = None
                invite_url = ""
                invite_secret = ""
            else:
                invite_url = (
                    f"{self.website_base_url}/redeem?id={invite_pairs.invite_id}"
                )
                invite_secret = invite_pairs.invite_secret

            res.send_response(200)
            res.send_header("Content-Type", "text/html")
            res.end_headers()
            res.wfile.write(
                template_render.render(
                    "invite_code.html.jinja",
                    {
                        "invite_url": invite_url,
                        "invite_secret": invite_secret,
                        "error_message": error_message,
                    },
                )
            )
