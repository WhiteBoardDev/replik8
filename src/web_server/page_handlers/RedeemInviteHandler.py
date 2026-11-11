from tracker.InvalidUserInputError import InvalidUserInputError
from tracker.registry.user_management.accept_invite import accept_invite
from tracker.registry.user_management.invites import InvitePairs
from web_server.page_handlers.common_ui_models.page_shell import (
    unauthenticated_page_shell_model,
)
from .form_parser_urlencoded import parse_request, ValueType, KeyType
from web_server.page_handlers.StatusCodeOnlyHandler import StatusCodeOnlyHandler
from typing import override, Literal, get_args
from tracker.registry.user_management.invites import is_invite_exists, peek_invite
from web_server.page_handlers.PageHandlerAbs import (
    PageHandlerAbs,
    RequestAttrs,
    ResponseFuncs,
    RoutingConfig,
    MatchType,
)
from web_server.templates import template_render


_unauthenticated_handler = StatusCodeOnlyHandler(401)
_bad_request_handler = StatusCodeOnlyHandler(400)
RedeemInviteFormInputName = Literal[
    "invite_id", "invite_secret", "username", "password", "confirm_password"
]


def _is_blank(key: str | None) -> bool:
    return key is not None and len(key) > 0


def _get_form_data_or_error_message(
    data: dict[KeyType, ValueType], field_name: str
) -> str | InvalidUserInputError:
    if (
        field_name not in data
        or not isinstance(data[field_name], str)
        or len(str(data[field_name])) == 0
    ):
        return InvalidUserInputError(f"Field {field_name} must be populated!")
    return str(data[field_name])


def _force_dict_value_as_str(dict, key: RedeemInviteFormInputName) -> str:
    val = dict[key]
    assert isinstance(val, str)
    return val


class RedeemInviteHandler(PageHandlerAbs):
    @override
    def get_routing_config(self) -> RoutingConfig:
        return RoutingConfig("/redeem", match_type=MatchType.EXACT)

    def _render_redeem_form(
        self,
        invite_id: str,
        req: RequestAttrs,
        res: ResponseFuncs,
        error_message: str | None,
    ):
        res.send_response(200)
        res.send_header("Content-Type", "text/html")
        res.end_headers()
        res.wfile.write(
            template_render.render(
                "redeem_invite.html.jinja",
                {
                    "page_shell": unauthenticated_page_shell_model(),
                    "invite_id": invite_id,
                    "error_message": error_message,
                },
            )
        )

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        if (
            "id" in req.query_params
            and len(req.query_params["id"]) == 1
            and is_invite_exists(req.query_params["id"][0])
        ):
            self._render_redeem_form(req.query_params["id"][0], req, res, None)
        else:
            _unauthenticated_handler.handle_get(req, res)

    def _invalid_value_for(self, key: str) -> str:
        return f"Invalid value for {key}!"

    @override
    def handle_post(self, req: RequestAttrs, res: ResponseFuncs) -> None:
        submitted_form = parse_request(req)
        if isinstance(submitted_form, InvalidUserInputError):
            _bad_request_handler.handle_get(req, res)
        else:
            form_data_parsed: dict[RedeemInviteFormInputName, str] = {}
            last_error = None
            for input_name in get_args(RedeemInviteFormInputName):
                if input_name not in submitted_form:
                    last_error = f"{input_name} not populated in form!"
                else:
                    val = submitted_form[input_name]
                    if not isinstance(val, str):
                        last_error = f"Expected {input_name} to be a string"
                    else:
                        form_data_parsed[input_name] = val

            if last_error is not None:
                if "invite_id" in form_data_parsed:
                    self._render_redeem_form(
                        form_data_parsed["invite_id"], req, res, last_error
                    )
                else:
                    _bad_request_handler.handle_get(req, res)
            elif _force_dict_value_as_str(
                form_data_parsed, "password"
            ) != _force_dict_value_as_str(form_data_parsed, "confirm_password"):
                self._render_redeem_form(
                    form_data_parsed["invite_id"],
                    req,
                    res,
                    "Password Confirm does not match!",
                )
            else:
                possible_error = accept_invite(
                    invite_pairs=InvitePairs(
                        form_data_parsed["invite_id"], form_data_parsed["invite_secret"]
                    ),
                    requested_username=form_data_parsed["username"],
                    new_password=form_data_parsed["password"],
                )
                if possible_error is None:
                    res.send_response(302)
                    res.send_header("location", "/")
                    res.end_headers()
                else:
                    self._render_redeem_form(
                        form_data_parsed["invite_id"], req, res, possible_error.message
                    )
