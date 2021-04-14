import asyncio
import json

import common as comm
from simple_handlers import bad_request_handler
from youtube_search_scraper import get_search_results_async

MAX_RESULTS = 5
SEARCH_QUERY_KEY = "term"


def handle_youtube_search(request: comm.Request) -> None:
    """Takes the user's search query, simulates a user search and returns a JSON response to the client.
    Very expensive."""
    search_terms = request.query.get(SEARCH_QUERY_KEY)

    if not search_terms:  # If is None or empty
        bad_request_handler(request, "Missing search term.")
    else:
        search_term = search_terms[0]

        http_handler = request.http_handler
        # Send the headers right away so the client knows that a response is coming.
        # Browsers can give up on the request otherwise, or attempt to send another request.
        http_handler.send_response(200)
        http_handler.send_header("Content-Type", "application/json")
        http_handler.end_headers()

        if search_term:
            # Forcing the asynchronous library calls to be synchronous
            results = asyncio.run(get_search_results_async(search_term))

            filtered_results = results[:MAX_RESULTS]
            str_results = json.dumps(filtered_results)
            http_handler.wfile.write(str_results.encode(comm.HTTP_ENCODING))

        # If the search term is empty, they bypassed front-end restrictions, so just drop request
