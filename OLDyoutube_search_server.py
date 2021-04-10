from __future__ import annotations
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Tuple
from typing import Dict, Callable
from urllib.parse import parse_qs, urlparse

import driver_pool
from youtube_search_handler import handle_youtube_search
from simple_handlers import bad_request_handler, index_handler
import common as comm

# An "interface" representing the expected signature of functions that handle requests
RequestHandler = Callable[[comm.Request], None]

# TODO: favicon.ico handler
GET_HANDLERS: Dict[str, RequestHandler] = \
    {"search": handle_youtube_search,
     "": index_handler}


class HTTPHandler(BaseHTTPRequestHandler):
    """Handles any incoming HTTP request to the server."""
    def do_GET(self) -> None:
        request = self.produce_standard_request()
        handler = GET_HANDLERS.get(request.path, bad_request_handler)

        handler(request)

    # TODO: Test what will need to change to handle POSTs.
    #   Does parsed_url.path start with a "/" for POST?
    def produce_standard_request(self) -> comm.Request:
        parsed_url = urlparse(self.path)
        return comm.Request(query=parse_qs(parsed_url.query),
                            path=parsed_url.path[1:],  # Drop leading /
                            http_handler=self)


class YoutubeSearchServer(ThreadingHTTPServer):
    """A basic server that handles incoming HTTP requests."""
    def __init__(self,
                 server_address: Tuple[str, int],
                 n_pooled_drivers: int,
                 have_headless_drivers: bool = True
                 ):
        super(YoutubeSearchServer, self).__init__(server_address=server_address,
                                                  RequestHandlerClass=HTTPHandler)
        self.driver_pool = driver_pool.FirefoxWebDriverPool(n_pooled_drivers, headless=have_headless_drivers)

    def __enter__(self) -> YoutubeSearchServer:
        return self

    def __exit__(self, *_) -> None:
        self.driver_pool.terminate()  # May block if a request is ongoing.
        self.server_close()
