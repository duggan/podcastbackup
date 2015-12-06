# Podcache

Back up podcasts with metadata from a feed URL. Progress indicator and resuming.
Hacky, only really tested against FeedBurner/libsyn feeds.

When you run it, you get a directory named after the podcast with a list of `mp3` files and `metadata.json` files.

```
tree /mnt/backups/podcast/
/mnt/backups/podcast/
├── bestshowever1.mp3.metadata.json
├── bestshowever1.mp3
├── bestshowever2.mp3.metadata.json
├── bestshowever2.mp3
├── bestshowever3.mp3.metadata.json
├── bestshowever3.mp3
```

The `metadata.json` files look like:

```json
{
    "text": "This is probably the best show yet!",
    "href": "http://bestshowever.cachefly.net/bestshowever/bestshowever42.mp3",
    "title": "Best Show Ever 42: All The Answers"
}
```

![Screenshot of Podcache downloading Hardcore History](http://i.imgur.com/pHdVEfi.png)

## Usage

1. Clone into a directory on your machine with `git clone https://gist.github.com/23c43febdc8fc393822d.git podcache`
2. Install dependencies with `pip install -r requirements.txt`
3. Run with `python podcache.py`

Works with Python 2 and 3.

## Ignores file

Drop a file named `.ignores` into the download directory of a particular podcast to skip downloading particular episodes.

Useful for skipping over broken / missing episodes. An example of the syntax is in the .ignores file with this repo.

