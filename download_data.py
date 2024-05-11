from typing import List, Tuple, Dict, Union, Tuple
import requests
import re
import json
from os import path
from bs4 import BeautifulSoup, NavigableString
from bs4.element import ResultSet, Tag, NavigableString
from time import sleep


SLEEP_SECONDS_BETWEEN_REQUESTS: float = 0.1
WORDLIST_FILE_PATH: str = "wordlist.json"
RESULT_FILE_PATH: str = "result.json"

DEFINITION_LINK_REGEX = re.compile(r'"/define\.php\?term=([^"]+)"')
BROWSE_CHARACTERS_REGEX = re.compile(r'"/browse\.php\?character=(.)"')
BROWSE_PAGENUMBER_REGEX = re.compile(r'"/browse\.php?[^";]+;page=(\d+)')

LOWERCASE_MONTH_NAME_TO_INT: Dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def download_index_for_letter(letter: str) -> List[str]:
    def get_page(page: int) -> Tuple[List[str], int]:
        print(f"+ + downloading wordlist for char {letter} page {page}")
        response = requests.get(f"https://www.urbandictionary.com/browse.php?character={letter}&page={page}")
        response.raise_for_status()
        definitions: List[str] = DEFINITION_LINK_REGEX.findall(response.text)
        last_page: int = max([
            int(i)
            # drop last one since its "last page" and therefore a random giant number
            for i in BROWSE_PAGENUMBER_REGEX.findall(response.text)[:-1]
        ] + [1])  # default
        return (definitions, last_page)

    print(f"+ downloading wordlist for char {letter}")
    wordlist, last_page = get_page(1)
    if last_page != 1:
        for page in range(2, last_page + 1):
            w, _ = get_page(page)
            wordlist += w
    return wordlist


def get_list_of_words() -> List[str]:
    if path.exists(WORDLIST_FILE_PATH):
        print("loading wordlist from file")
        with open(WORDLIST_FILE_PATH, "r") as fp:
            return json.load(fp)

    print("downloading wordlist")
    response = requests.get('https://www.urbandictionary.com/')
    response.raise_for_status()
    html: str = response.text  # seperate line due to linter bugs
    characters: List[str] = BROWSE_CHARACTERS_REGEX.findall(html)

    wordlist: List[str] = []
    for character in characters:
        sleep(SLEEP_SECONDS_BETWEEN_REQUESTS)
        wordlist += download_index_for_letter(character)

    print("saving wordlist to wordlist.json")
    with open(WORDLIST_FILE_PATH, "w") as fp:
        json.dump(wordlist, fp)
    return wordlist


def download_definitions_for(word: str) -> List[Dict[str, Union[str, List[str], int]]]:
    # TODO
    response = requests.get(f"https://www.urbandictionary.com/define.php?term={word}")
    response.raise_for_status()
    soup: BeautifulSoup = BeautifulSoup(response.text, features="html.parser")
    definitions: ResultSet = soup.findAll(class_="definition")
    result: List[Dict[str, Union[str, List[str], int]]] = []
    for definition in definitions:
        result.append(parse_definition_entry(definition))

    # download up-/downvotes
    # here and not in each def since the API allow batch-requests and we reduce server-load this way
    def_ids: List[int] = [i["id"] for i in result]  # type: ignore
    votes: Dict[int, Tuple[int, int]] = get_votes(def_ids)
    for i in result:
        votes_for_i: Tuple[int, int] = votes[i["id"]]  # type: ignore
        i["upvotes"] = votes_for_i[0]
        i["downvotes"] = votes_for_i[1]

    return result


def parse_definition_entry(html_tag: Tag) -> Dict[str, Union[int, str, List[str]]]:
    word = html_tag.find(class_="word")
    assert word is not None, "HTML definition does not contain a 'word'"
    definition_id: int = int(word["id"])  # type: ignore
    meaning = html_tag.find(class_="meaning")
    assert meaning is not None, "HTML definition does not contain a 'meaning'"
    example = html_tag.find(class_="example")
    examples: List[str] = []
    if example is not None:
        examples = [
            BeautifulSoup(i, features="html.parser").text
            for i in str(example).split("<br/>")
            if not i.isspace()
        ]
    contributor = html_tag.find(class_="contributor")
    assert contributor is not None, "HTML definition does not contain a 'contributor'"
    authorname: (Tag | NavigableString | None) = contributor.find(name="a")  # type: ignore
    assert authorname is not None, "HTML definition does not contain a 'contributor>a'"
    date_raw: List[str] = contributor.text.split(" ")[-3:]
    buttons: ResultSet = html_tag.findAll(name="button")
    assert len(buttons) == 2, f"UD changed how many buttons a entry has (expected 2, got {len(buttons)})"

    return {
        "id": definition_id,
        "word": word.text,
        "meaning": meaning.text,
        "examples": examples,
        "author_name": authorname.text,
        "definition_date": f'{date_raw[2]}-{LOWERCASE_MONTH_NAME_TO_INT[date_raw[0].lower()]:02}-{int(date_raw[1].strip(",")):02}',
    }


def get_votes(definition_ids: List[int]) -> Dict[int, Tuple[int, int]]:
    ids_str: str = ",".join([str(i) for i in definition_ids])
    response = requests.get(f'https://api.urbandictionary.com/v0/uncacheable?ids={ids_str}')
    response.raise_for_status()
    data = response.json()["thumbs"]
    result: Dict[int, Tuple[int, int]] = {}
    for i in data:
        result[i["defid"]] = (i["up"], i["down"])
    return result


def download_all(wordlist: List[str]) -> Dict[str, List[Dict[str, Union[List[str], str, int]]]]:
    print("Downloading all definitions")
    result: Dict[str, List[Dict[str, Union[List[str], str, int]]]] = {}
    total_defs: int = len(wordlist)
    idx: int = 0
    while idx < total_defs:
        word: str = wordlist[idx]
        print(f"+ downloading definition {word} ({idx + 1}/{total_defs})")

        result[word] = download_definitions_for(word)

        if idx % 1000 == 0:
            print("saving result section")
            with open(f"until_idx_{idx}.json", "w") as f:
                json.dump(result, f)
            result = {}
        idx += 1

        sleep(SLEEP_SECONDS_BETWEEN_REQUESTS)

    return result


if __name__ == "__main__":
    wordlist: List[str] = get_list_of_words()
    download_all(wordlist)
