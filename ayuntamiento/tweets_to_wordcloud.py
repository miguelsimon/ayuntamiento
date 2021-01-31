import argparse
import json
import re
import string
from collections import defaultdict
from typing import Dict, Iterable

from stop_words import get_stop_words
from wordcloud import WordCloud

STOP_WORDS = set(get_stop_words("es")).union(set(get_stop_words("ca")))
STOP_WORDS = STOP_WORDS.union(["rt", "‘fue", "“entre", "valencia", "valenciana"])


def file_to_texts(f) -> Iterable[str]:
    for line in f:
        yield json.loads(line.strip())["text"]


def get_frequencies(texts: Iterable[str]) -> Dict[str, int]:
    res: Dict[str, int] = defaultdict(int)
    for text in texts:
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r"[^\w\s]", "", text, re.UNICODE)
        for term in text.split():
            normalized = term.lower()
            if normalized not in STOP_WORDS:
                res[normalized] += 1
    return res


def make_cloud(frequencies: Dict[str, int]) -> WordCloud:
    wordcloud = WordCloud(width=800, height=600).generate_from_frequencies(frequencies)

    return wordcloud


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
        help="name of output image",
    )
    args = parser.parse_args()

    with open(args.in_file, "r") as in_f:
        texts = file_to_texts(in_f)
        frequencies = get_frequencies(texts)

        wordcloud = make_cloud(frequencies)
        wordcloud.to_file(args.out_file)
