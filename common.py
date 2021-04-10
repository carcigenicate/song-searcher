from http.server import BaseHTTPRequestHandler
from typing import NamedTuple, List, Dict, AnyStr
from pathlib import Path

HTTP_ENCODING = "ascii"

RUN_PATH = Path(__file__).parent.absolute()

print()

class Request(NamedTuple):
    """Holds all the pre-processed information that's required to handle a request."""
    query: Dict[str, List[str]]
    path: str
    http_handler: BaseHTTPRequestHandler


def send_simple_response(request: Request, response_code: int, headers: Dict[str, str], data: AnyStr = "") -> None:
    http_handler = request.http_handler
    http_handler.send_response(response_code)
    for k, v in headers.items():
        http_handler.send_header(k, v)
    http_handler.end_headers()
    encoded_data = data if isinstance(data, bytes) else data.encode(HTTP_ENCODING)  # write requires bytes
    http_handler.wfile.write(encoded_data)


def send_html_page(request: Request, page_path: str) -> bool:
    """Sends the html page indicated by page_path.
    A potentially dangerous function that allows for directory traversal and sending arbitrary files to the client.
      No sanitization is done on input. Do not pass untrusted data as page_path.
    """
    try:
        # RUN_PATH is so relative page_paths don't break when server is started from a directory
        #   other than the project root.
        with open(RUN_PATH / page_path, "rb") as f:
            file = f.read()  # TODO: Read incrementally to avoid holding all in memory? Holds up file.
    except FileNotFoundError:
        return False

    send_simple_response(request, 200, {"Content-Type": "text/html"}, file)
    return True
