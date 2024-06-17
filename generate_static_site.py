#!/usr/bin/env python3
# generate a static html site from the data
# usage: python3 ./generate_static_site.py ud.json

# this generator enumerates pages.
# why not escape or base64 encode the names or something?
# because theres a 422 utf-8 bytes long word and linux ext4 only allows 255
# character long filenames (see linux-kernel/fs/ext4/ext4.h EXT4_NAME_LEN)

from typing import List, Dict, Union, Generator
from html import escape as he
from urllib.parse import unquote
from base64 import urlsafe_b64encode
import json


def main(json_file: str) -> None:
    with open(json_file) as fh:
        json_data = json.load(fh)

    all_words: List[str] = list(set(sum((i["pagenames"] for i in json_data), [])))
    all_words.sort()

    print("generating index..")
    index_html: str = generate_index(all_words)
    with open("./static_html/index.html", "w") as fh:
        fh.write(index_html)
    del index_html

    print("generating words..")
    one_percent = len(all_words) // 100
    cur_percent = 0
    for idx, word in enumerate(all_words):
        word_page_html: str = generate_word_page(
            word,
            (i for i in json_data if word in i["pagenames"])
        )
        with open(f"./static_html/{idx_to_filename(idx)}.html", "w") as fh:
            fh.write(word_page_html)
        del word_page_html
        if idx % one_percent == 0:
            cur_percent += 1
            print(f"{cur_percent}% done")


def generate_index(all_words: List[str]) -> str:
    return ''.join([
        '<!DOCTYPE HTML><html><head>',
        '<title>UDOffline Index</title>',
        '<link href="style.css" rel="stylesheet">',
        '</head><body>',
        '<h1>UDOffliner Index</h1>',
        '<p>Use CRTL+f</p>',
        '<ul>',
        *(f'<li><a href="{idx_to_filename(idx)}.html">{he(unquote(word))}</a></li>' for idx, word in enumerate(all_words)),
        '</ul>',
        '</body></html>',
   ])


def generate_word_page(pagename: str, definitions: Generator[Dict[str, Union[str, int, List[str]]], None, None]) -> str:
    definition_html_list: List[str] = []
    for definition in definitions:
        assert isinstance(definition["examples"], list)
        assert isinstance(definition["word"], str)
        assert isinstance(definition["meaning"], str)
        assert isinstance(definition["author_name"], str)
        assert isinstance(definition["upvotes"], int)
        assert isinstance(definition["downvotes"], int)
        examples_html: str = "".join((
            f'<p>{he(example)}</p>' for example in definition["examples"]
        ))
        definition_html_list.append("".join([
            '<div class="def">'
            f'<h2>{he(definition["word"])}</h2>'
            f'<p>{he(definition["meaning"])}</p>'
            f'<div class="ex">{examples_html}</div>'
            f'<div class="meta"><b>Author:</b> {he(definition["author_name"])} <b>Upvotes:</b> {definition["upvotes"]} <b>Downvotes:</b> {definition["downvotes"]}</div>'
            '</div>'
        ]))

    return "".join([
        '<!DOCTYPE HTML><html><head>',
        f'<title>{he(unquote(pagename))}</title>',
        '<link href="style.css" rel="stylesheet">',
        '</head><body>',
        '<nav><a href="index.html">index</a></nav>',
        f'<h1>{he(unquote(pagename))}</h1>',
        ''.join(definition_html_list),
        '</body></html>',
    ])


def idx_to_filename(idx: int) -> str:
    return urlsafe_b64encode(idx.to_bytes(length=32)).decode("ascii").rstrip("=")


if __name__ == "__main__":
    from sys import argv
    main(argv[1])
