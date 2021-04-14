import json
import logging

from paho.mqtt import MQTTException
from paho.mqtt.publish import single as publish_single

import common as comm

REQUEST_TOPIC = "request"
REQUEST_PARAMETER = "yid"

HOSTNAME = "174.0.233.205"  # TODO: Change back to localhost
USERNAME = "reproject"
PASSWORD = "reproject"


# To prevent 400 errors when the browser auto-attempts to get favicon.
def favicon_request_handler(request: comm.Request) -> None:
    comm.send_simple_response(request,
                              200,
                              {})


def song_request_handler(request: comm.Request) -> None:
    song_request = request.query.get(REQUEST_PARAMETER)
    print("HANDLER ENTERED!")
    if not song_request:
        print("BAD REQUEST!")
        bad_request_handler(request, "Missing youtube video ID.")
    else:
        try:
            auth = {"username": USERNAME, "password": PASSWORD}
            print("PUBLISHING!")
            publish_single(REQUEST_TOPIC, song_request[0], auth=auth, hostname=HOSTNAME)
            print("PUBLISHED!")
            comm.send_simple_response(request,
                                      200,
                                      {"Content-Type": "application/json"},
                                      json.dumps({"success": "Request Received"}))
            print("RESPONSE SENT!")
        except ConnectionRefusedError:
            logging.warning("MQTT server rejected connection/is not started.")
            bad_request_handler(request, "Unable to contact broker. Message was not passed on.")
        except MQTTException as e:
            logging.warning(f"Generic MQTT error: {e}")
            bad_request_handler(request, "Unable to contact broker. Message was not passed on.")



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