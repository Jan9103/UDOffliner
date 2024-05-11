# UDOffliner

Create a backup of the UrbanDictionary for archiving purposes.

### Features:

- [x] generate a `wordlist.json`
- [x] download all definitions into json files
  - [x] description
  - [x] examples
  - [x] date
  - [x] author
  - [x] votes
- [ ] generate html-file directory for nginx/...

### Notices:

- in order to not DDOS the server it sleeps between each request and therefore takes at least 3 days.
- if anything goes wrong it throws an error, never catches it, and crashes. since it regularly (every 1000 words) saves it shouldnt be too bad.
- this uses webscraping and therefore might break at any point if UD changes their html layout.

### Dependencies:

- Python3 (programming language) (preferably 3.11 since that one has been tested)
- BeautifulSoup4 (html parser)
- requests (http request sender)

### Usage:

1. clone this git repo and open a terminal in it ([tutorial](https://www.atlassian.com/git/tutorials/setting-up-a-repository/git-clone))
2. check the code for viruses. no it does not contain any, but i could be lying and you should always check.
3. install all dependencies (example method: [install nix](https://nixos.org/download/) and run `nix-shell`).
4. run `python3 download_data.py`.
5. have fun with your douzen `json` files.
  * [nushell](https://github.com/nushell/nushell) is great for exploring and converting data.
  * `gzip` can be used to compress them and reduce the storage space needed.
