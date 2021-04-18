import json
import logging

import common as comm


# To prevent 400 errors when the browser auto-attempts to get favicon.
def favicon_request_handler(request: comm.Request) -> None:
    comm.send_simple_response(request,
                              200,
                              {})


def bad_request_handler(request: comm.Request, reason: str = "") -> None:
    """Outputs a 400 JSON response with an optional message."""
    message_ending = f": {reason}" if reason else ""
    comm.send_simple_response(request,
                              400,
                              {"Content-Type": "application/json"},
                              json.dumps({"error": f"Bad Request{message_ending}"}))


def index_handler(request: comm.Request) -> None:
    """Serves the index, or an error if the index can't be found."""
    result = comm.send_html_page(request, "index.html")

    if not result:
        logging.warning("Failed to load page: index.html")
        bad_request_handler(request, "Could not load page.")
