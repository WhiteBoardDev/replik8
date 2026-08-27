import page_handlers
import page_handlers
from typing import Callable
import data_manager
import template_render
from http.server import HTTPServer, BaseHTTPRequestHandler
from  page_handlers import index, download
import routes

_route_handlers: dict[str,
Callable[[], None]] = {
    "": index.handle,
    routes.api_download_file_path : download.handle
}



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(template_render.render("index.html", {
            "directory_list": data_manager.list_contents(None)
        }))




server_address_bind = ('localhost', 8080)
httpd = HTTPServer(server_address_bind, SimpleHTTPRequestHandler)
print("starting httpserver")
httpd.serve_forever()
print("server exited")