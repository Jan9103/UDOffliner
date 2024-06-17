#!/usr/bin/env python3
# convert a unified json (unify.py) into a sqlite3 file
# usage: python3 toSqlite defs.json defs.db

from collections.abc import Iterable
import sqlite3
import json
from os import path
from sys import exit
from typing import List, Dict, Union, Tuple, Generator

def main(json_file: str, sqlite_file: str) -> None:
    if path.exists(sqlite_file):
        print("ERROR: sqlite file already exists. updating is not yet supported. delete the file first.")
        exit(1)

    # === LOAD JSON ===
    print("Loading json..")
    with open(json_file) as fh:
        json_data: List[Dict[str, Union[str, int, List[str]]]] = json.load(fh)
    # not a perfect validation, but trips on "until_idx_*.json" and "wordlist.json" files
    assert isinstance(json_data, list), "Invalid json file"
    assert isinstance(json_data[0], dict), "Invalid json file"

    # === CONNECT SQL ===
    print("Connecting SQLite..")
    # no need for a context-manager. if it dies it dies
    con: sqlite3.Connection = sqlite3.connect(sqlite_file)
    cur: sqlite3.Cursor = con.cursor()

    # === INSERT DEFINITIONS ===
    print("Creating Definitons SQL table..")
    cur.execute("""
        CREATE TABLE Definitions (
            DefinitionId int NOT NULL PRIMARY KEY,
            Word varchar(255) NOT NULL,
            Meaning varchar(255) NOT NULL,
            AuthorName varchar(255) NOT NULL,
            DefinitionDate date NOT NULL,
            Upvotes int NOT NULL,
            Downvotes int NOT NULL
        )
    """)
    print("Inserting Definiton data into SQL..")
    sql_definition_data: Generator[Tuple[int, str, str, str, str, int, int], None, None] = (
        (
            i["id"],
            i["word"],
            i["meaning"],
            i["author_name"],
            i["definition_date"],
            i["upvotes"],
            i["downvotes"],
        )  # type: ignore
        for i in json_data
    )
    cur.executemany(
        "INSERT INTO Definitions VALUES (?, ?, ?, ?, ?, ?, ?)",
        sql_definition_data,
    )
    del sql_definition_data  # clean ram

    # === INSERT EXAMPLES ===
    print("Creating Examples SQL Table..")
    cur.execute("""
        CREATE TABLE Examples (
            ExampleId int,
            ExampleText varchar(255),
            DefinitionId int,
            PRIMARY KEY (ExampleId),
            CONSTRAINT FK_DefinitionId FOREIGN KEY (DefinitionID) REFERENCES Definitions(DefinitionId)
        )
    """)
    print("Inserting Examples into SQL..")
    for definition in json_data:
        id: int = definition["id"]  # type: ignore
        examples: List[str] = definition["examples"]  # type: ignore
        for example in examples:
            cur.execute(
                "INSERT INTO Examples (DefinitionId, ExampleText) VALUES (?, ?)",
                (id, example),
            )

    # === INSERT PAGENAME ===
    print("Creating Pagename SQL Table..")
    cur.execute("""
        CREATE TABLE Pagenames (
            Pagename varchar(255) NOT NULL,
            DefinitionId int NOT NULL,
            PRIMARY KEY ( Pagename, DefinitionId ),
            FOREIGN KEY ( DefinitionId ) REFERENCES [Definitions] (DefinitionId)
        )
    """)
    print("Insert Pagename into SQL..")
    for definition in json_data:
        pagenames: List[str] = definition["pagenames"]  # type: ignore
        cur.executemany(
            "INSERT INTO Pagenames VALUES (?, ?)",
            ((i, definition["id"]) for i in pagenames)
        )

    # === CLEANUP ===
    print("Finishing touches..")
    con.commit()
    con.close()
    print("Done.")


if __name__ == "__main__":
    from sys import argv
    main(argv[1], argv[2])
