from src.users import authenticate_user
from .PageHandlerAbs import ResponseFuncs
import base64

_basic = "Basic "

def handle(authentication_header: str | None, res: ResponseFuncs) -> str | None:
    if authentication_header is not None and authentication_header.startswith(_basic):
        prefix_removed = authentication_header.removeprefix(_basic)
        decoded = base64.b64decode(prefix_removed).decode("utf-8")
        parts = decoded.split(':')
        assert len(parts) == 2
        user = parts[0]
        password = parts[1]
        user_id = authenticate_user(user, password)
        if user_id is not None:
            return user_id
    _send_unauth(res)
    return None



def _send_unauth(res: ResponseFuncs):
    res.send_response(401)
    res.send_header("WWW-Authenticate", "Basic realm=\"Protected Area\"")
            
