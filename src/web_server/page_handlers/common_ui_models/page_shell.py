from tracker.registry.user_management.users import get_user_by_id
from web_server.page_handlers.PageHandlerAbs import RequestAttrs
from web_assets import css_assets, js_assets


def page_shell_model(req: RequestAttrs):
    assert req.authenticated_user_id is not None
    user_record = get_user_by_id(req.authenticated_user_id)
    assert user_record is not None
    return {
        "link_includes": [
            {"src": x.local_destination(), "integrity": x.integrity_hash}
            for x in css_assets
        ],
        "script_includes": [
            {"src": x.local_destination(), "integrity": x.integrity_hash}
            for x in js_assets
        ],
        "site_name": "Replik8",
        "username": user_record.name,
    }


def unauthenticated_page_shell_model():
    return {
        "link_includes": [
            {"src": x.local_destination(), "integrity": x.integrity_hash}
            for x in css_assets
        ],
        "script_includes": [
            {"src": x.local_destination(), "integrity": x.integrity_hash}
            for x in js_assets
        ],
    }
