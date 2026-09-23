from web_server.page_handlers.PageHandlerAbs import ResponseFuncs

def parse_cookie_header(raw_cookie_header: str) -> dict[str,str]:
    result = {}
    for kv_pair in raw_cookie_header.split(';'):
        parts = kv_pair.split('=')
        assert len(parts) == 2, "Cookie header malformed"
        result[parts[0]] = parts[1]
    return result


def set_cookie(res: ResponseFuncs, name: str, value: str):
    # TODO - use "secure" cookie too but only when https enabled
    res.send_header("Set-Cookie", f"{name}={value}; SameSite=Strict; HttpOnly")
