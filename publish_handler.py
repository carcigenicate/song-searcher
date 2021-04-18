import json
import logging
import ssl

from paho.mqtt import MQTTException
from paho.mqtt.publish import single as publish_single

import common as comm
from simple_handlers import bad_request_handler
from broker_config import Config


REQUEST_PARAMETER = "yid"

CONFIG_PATH = "./broker.cfg"
CONFIG = Config.from_file(CONFIG_PATH)


def song_request_handler(request: comm.Request) -> None:
    song_request = request.query.get(REQUEST_PARAMETER)
    if not song_request:
        bad_request_handler(request, "Missing youtube video ID.")
    else:
        try:
            auth = {"username": CONFIG.username, "password": CONFIG.password}
            publish_single(CONFIG.topic,
                           song_request[0],
                           auth=auth,
                           hostname=CONFIG.host,
                           port=CONFIG.port,
                           tls={"tls_version": ssl.PROTOCOL_TLS},
                           keepalive=10,  # Publish timeout
                           qos=2)
            comm.send_simple_response(request,
                                      200,
                                      {"Content-Type": "application/json"},
                                      json.dumps({"success": "Request Received"}))
        # These errors will only be thrown if the hostname is something obviously wrong like "localhost".
        except ConnectionRefusedError:
            logging.warning("MQTT server rejected connection/is not started.")
            bad_request_handler(request, "Unable to contact broker. Message was not passed on.")
        except MQTTException as e:
            logging.warning(f"Generic MQTT error: {e}")
            bad_request_handler(request, "Unable to contact broker. Message was not passed on.")

