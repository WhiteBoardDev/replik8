from src.page_handlers.PageHandlerAbs import PageHandlerAbs, RequestAttrs, ResponseFuncs
from typing import override


class StatusCodeOnlyHandler(PageHandlerAbs):

    def __init__(self, statusCode: int):
        self.status = statusCode

    def get_routing_config(self):
        raise NotImplementedError()

    @override
    def handle_get(self, req: RequestAttrs, res: ResponseFuncs):
        res.send_response(self.status)
        res.end_headers()
        