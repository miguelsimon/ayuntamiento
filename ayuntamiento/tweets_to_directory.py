import datetime as dt
import json
import logging
import os
import time
from typing import Any, Dict, Iterable

from TwitterAPI import TwitterAPI, TwitterConnectionError, TwitterRequestError

logger = logging.getLogger(__name__)


def stream_to_directory(directory: str, stream: Any, max_per_file: int = 1000) -> None:
    while True:
        stamp = dt.datetime.utcnow()
        filename = stamp.strftime("%Y-%m-%d-%H-%M-%S-%f.json")
        path = os.path.join(directory, filename)
        logger.info("opening {0}".format(path))
        with open(path, "w") as f:
            for i, obj in enumerate(stream):
                json.dump(obj, f)
                f.write("\n")
                f.flush()

                if i == max_per_file:
                    logger.info("{0}: {1} messages written".format(path, i))
                    break


def make_stream(api: TwitterAPI, params: Dict) -> Iterable[Dict]:
    """
    Handle reconnect logic here.

    Adapted from http://geduldig.github.io/TwitterAPI/faulttolerance.html
    """
    while True:
        try:
            iterator = api.request("statuses/filter", params).get_iterator()
            for item in iterator:
                yield item
                if "disconnect" in item:
                    event = item["disconnect"]
                    if event["code"] in [2, 5, 6, 7]:
                        # something needs to be fixed before re-connecting
                        raise Exception(event["reason"])
                    else:
                        logger.warning("disconnect {0}".format(event))
                        # temporary interruption, re-try request
                        break
        except TwitterRequestError as e:
            logger.warning("TwitterRequestError {0}".format(e))
            if e.status_code < 500:
                # something needs to be fixed before re-connecting
                raise e
            else:
                # temporary interruption, re-try request after sleeping
                time.sleep(60)
        except TwitterConnectionError as e:
            logger.warning("TwitterConnectionError {0}".format(e))
            # temporary interruption, re-try request immediately
            pass


def dump(
    directory: str,
    consumer_key: str,
    consumer_secret: str,
    access_token_key: str,
    access_token_secret: str,
    track_query: Dict,
) -> None:

    api = TwitterAPI(
        consumer_key, consumer_secret, access_token_key, access_token_secret
    )
    stream = make_stream(api, track_query)
    stream_to_directory(directory, stream)


if __name__ == "__main__":
    env = os.environ

    logging.basicConfig(level=logging.DEBUG)

    query_params = {"track": "pizza"}

    track_query_str = env["TRACK_QUERY"]
    track_query = json.loads(track_query_str)

    dump(
        directory=env["TARGET_DIRECTORY"],
        consumer_key=env["CONSUMER_KEY"],
        consumer_secret=env["CONSUMER_SECRET"],
        access_token_key=env["ACCESS_TOKEN_KEY"],
        access_token_secret=env["ACCESS_TOKEN_SECRET"],
        track_query=track_query,
    )
