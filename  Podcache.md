# Podcache

Back up podcasts with metadata from a feed URL. Progress indicator and resuming.
Hacky, only really tested against libsyn feeds.

## Usage

1. Clone into a directory on your machine with `git clone https://gist.github.com/23c43febdc8fc393822d.git podcache`
2. Install dependencies with `pip install -r requirements.txt`
3. Run with `python podcache.py`

Works with Python 2 and 3.

## Ignores file

Drop a file named `.ignores` into the download directory of a particular podcast to skip downloading particular episodes.

Useful for skipping over broken / missing episodes. An example of the syntax is in the .ignores file with this repo.