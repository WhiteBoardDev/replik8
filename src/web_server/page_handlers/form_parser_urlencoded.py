from urllib.parse import parse_qs
from tracker.InvalidUserInputError import InvalidUserInputError
from web_server.page_handlers.PageHandlerAbs import RequestAttrs


_content_type = "application/x-www-form-urlencoded"
_max_content_length = 5_000

type KeyType = str
type ValueType = str | int | bool


def _to_value_type(raw_val: bytes) -> ValueType:
    decoded_str = raw_val.decode()
    if decoded_str.isdigit():
        return int(decoded_str)
    elif decoded_str.lower().strip() in ["false", "true"]:
        return decoded_str.lower().strip() == "true"
    else:
        return decoded_str


def parse_request(
    req: RequestAttrs,
) -> dict[KeyType, ValueType] | InvalidUserInputError:
    if req.content_type is None or req.content_type != _content_type:
        return InvalidUserInputError(f"Content type must be {_content_type}")
    elif req.content_length is None:
        return InvalidUserInputError("Request must have a content-length header")
    elif req.content_length >= _max_content_length:
        return InvalidUserInputError("Message body too large. Refusing")
    else:
        raw = req.rfile.read(req.content_length)
        qs_parsed = parse_qs(raw)
        typed_parsed = {
            k.decode(): _to_value_type(qs_parsed[k][0]) for k in qs_parsed.keys()
        }
        return typed_parsed
