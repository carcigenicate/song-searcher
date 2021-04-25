from __future__ import annotations
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Tuple
from typing import Dict, Callable
from urllib.parse import parse_qs, urlparse

from youtube_search_handler import handle_youtube_search
from simple_handlers import bad_request_handler, index_handler
from publish_handler import song_request_handler
import common as comm

# An "interface" representing the expected signature of functions that handle requests
RequestHandler = Callable[[comm.Request], None]


GET_HANDLERS: Dict[str, RequestHandler] = \
    {"": index_handler,
     "search": handle_youtube_search,
     "request": song_request_handler}


class HTTPHandler(BaseHTTPRequestHandler):
    """Handles any incoming HTTP request to the server."""
    def do_GET(self) -> None:
        request = self.produce_standard_request()
        handler = GET_HANDLERS.get(request.path, bad_request_handler)
        handler(request)

    def produce_standard_request(self) -> comm.Request:
        parsed_url = urlparse(self.path)
        return comm.Request(query=parse_qs(parsed_url.query),
                            path=parsed_url.path[1:],  # Drop leading /
                            http_handler=self)


class YoutubeSearchServer(ThreadingHTTPServer):
    """A basic server that handles incoming HTTP requests."""
    def __init__(self, server_address: Tuple[str, int]):
        super(YoutubeSearchServer, self).__init__(server_address=server_address,
                                                  RequestHandlerClass=HTTPHandler)

    def __enter__(self) -> YoutubeSearchServer:
        return self

    def __exit__(self, *_) -> None:
        self.server_close()
