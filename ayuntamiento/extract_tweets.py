import argparse
import json
import os
from typing import Dict, Iterable, Set


def file_to_iterator(path: str) -> Iterable[Dict]:
    with open(path, "r") as f:
        for line in f:
            yield json.loads(line.strip())


def dump_to_iterator(directory: str) -> Iterable[Dict]:
    for name in os.listdir(directory):
        if name.endswith(".json"):
            filename = os.path.join(directory, name)
            for datum in file_to_iterator(filename):
                yield datum


def get_compliant_tweets(directory: str) -> Iterable[Dict]:
    """
    Yield a stream of tweets from a data dump.

    Scrub deleted tweets and geo information for compliance with
    https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/overview
    """
    deleted: Set[int] = set()
    scrubbed_geo_users: Set[int] = set()

    for datum in dump_to_iterator(directory):
        if "delete" in datum:
            deleted.add(datum["status"]["id"])

        if "scrub_geo" in datum:
            scrubbed_geo_users.add(datum["scrub_geo"]["user_id"])

    for datum in dump_to_iterator(directory):
        if "text" in datum:  # is a tweet
            if datum["id"] not in deleted:
                user_id = datum["user"]["id"]

                if user_id in scrubbed_geo_users:
                    datum["coordinates"] = None

                yield datum


def dump_to_tweet_file(directory: str, f) -> None:
    """
    Transform a data dump into a newline-separated file of tweets
    """

    for tweet in get_compliant_tweets(directory):
        json.dump(tweet, f)
        f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--read_dir", required=True, help="path to directory containing the dump"
    )
    parser.add_argument(
        "--out_file",
        required=True,
        help="path to output file",
    )
    args = parser.parse_args()

    with open(args.out_file, "w") as f:
        dump_to_tweet_file(args.read_dir, f)
