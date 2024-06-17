#!/usr/bin/env python3
# convert a bunch of until_idx_*.json files into a single defs.json file to ease working with it
# usage: python3 unify.py ...FILES
# example: python3 unify.py until_idx_*.json > defs.json

import json
from typing import List, Dict, Union


def main(files: List[str]) -> List[Dict[str, Union[str, int, List[str]]]]:
    result: List[Dict[str, Union[str, int, List[str]]]] = []
    for file in files:
        with open(file) as fh:
            filecontents: Dict[str, List[Dict[str, Union[int, str, List[str]]]]] = json.load(fh)
        for pagename, definitions in filecontents.items():
            for definition in definitions:
                # find duplicates (for some reason some things are under 2 page names
                # example: 15363898 at O%20WEL and O%20wel%20Dorito%21
                id: int = definition["id"]  # type: ignore
                for i in result:
                    if i["id"] == id:
                        # don't ask me why, but this if is necesary
                        if pagename not in i["pagenames"]:  # type: ignore
                            i["pagenames"].append(pagename)  # type: ignore
                        break
                else:
                    result.append({"pagenames": [pagename], **definition})
    return result


if __name__ == "__main__":
    print(json.dumps(main(__import__("sys").argv[1:])))
