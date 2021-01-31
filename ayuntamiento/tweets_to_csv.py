import argparse
import csv
import datetime as dt
import json
from typing import Dict, Iterable, NamedTuple


class Row(NamedTuple):
    date: str
    time: str
    text: str
    screen_name: str
    name: str


def tweet_to_row(tweet: Dict) -> Row:
    stamp = dt.datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
    return Row(
        date=stamp.strftime("%Y-%m-%d"),
        time=stamp.strftime("%H:%M:%S"),
        text=tweet["text"],
        screen_name=tweet["user"]["screen_name"],
        name=tweet["user"]["name"],
    )


def file_to_tweets(f) -> Iterable[Dict]:
    for line in f:
        yield json.loads(line.strip())


def tweets_to_rows(tweets: Iterable[Dict]) -> Iterable[Row]:
    for tweet in tweets:
        yield tweet_to_row(tweet)


def dump_to_csv(rows: Iterable[Row], out_f) -> None:
    writer = csv.DictWriter(out_f, fieldnames=Row._fields)
    writer.writeheader()

    for row in rows:
        writer.writerow(row._asdict())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in_file",
        required=True,
        help="path to file containing newline-separated tweets",
    )
    parser.add_argument(
        "--out_file",
        required=True,
        help="path to output file",
    )
    args = parser.parse_args()

    with open(args.in_file, "r") as in_f:
        with open(args.out_file, "w") as out_f:
            tweets = file_to_tweets(in_f)
            rows = tweets_to_rows(tweets)
            dump_to_csv(rows, out_f)
