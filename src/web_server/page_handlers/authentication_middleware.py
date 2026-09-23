from web_server.page_handlers.cookies import parse_cookie_header, set_cookie
from tracker.users import authenticate_user
from .PageHandlerAbs import ResponseFuncs
import base64
import uuid
_basic = "Basic "


"""
Simple in memory session store to avoid hashing the plaintext credentials every time 
TODO - convert this to an LRU cache!!
TODO - this in memory store is of unbounded size
"""
_session_store: dict[str, str] = {}

_session_cookie_name = 'rpl_sess'

def handle(authentication_header: str | None, cookie_header: str | None, res: ResponseFuncs) -> str | None:

    # Attempt shortcut cache lookup
    if cookie_header is not None:
        cookies = parse_cookie_header(cookie_header)
        if _session_cookie_name in cookies:
            session_key = cookies[_session_cookie_name]
            if session_key in _session_store:
                return _session_store[session_key]


    if authentication_header is not None and authentication_header.startswith(_basic):
        prefix_removed = authentication_header.removeprefix(_basic)
        decoded = base64.b64decode(prefix_removed).decode("utf-8")
        parts = decoded.split(':')
        assert len(parts) == 2
        user = parts[0]
        password = parts[1]
        user_id = authenticate_user(user, password)
        if user_id is not None:
            # Success!
            session_key = uuid.uuid4().hex
            set_cookie(res, _session_cookie_name, session_key)
            _session_store[session_key] = user_id
            return user_id
    _send_unauth(res)
    return None



def _send_unauth(res: ResponseFuncs):
    res.send_response(401)
    res.send_header("WWW-Authenticate", "Basic realm=\"Protected Area\"")
            
