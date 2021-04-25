#!/usr/bin/env python3
"""
The root of the server. Parses and standardizes incoming requests, then dispatches out to the appropriate handlers
  based on the request.
"""
import logging

from argparse import ArgumentParser

from youtube_search_server import YoutubeSearchServer


DEFAULT_SERVER_PORT = 5555


def start_server(port: int) -> None:
    # This will block for several seconds as the internal pool is instantiated.
    with YoutubeSearchServer(("", port)) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down server.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_SERVER_PORT,
                        help="The port to have the server listen on.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)

    start_server(args.port)
