
from page_handlers.PageHandlerAbs import ResponseFuncs, RequestAttrs
from page_handlers.PageHandlerAbs import PageHandlerAbs

class StatusCodeOnlyHandler(PageHandlerAbs):

    def __init__(self, statusCode: int):
        self.status = statusCode

    def get_routing_config(self):
        raise NotImplementedError()

    def handle(self, req: RequestAttrs, res: ResponseFuncs):
        res.send_response(self.status)
        res.end_headers()
        