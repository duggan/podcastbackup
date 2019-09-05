# -*- coding: utf-8 -*-

import os
import re
import argparse
import signal
import json
import logging
from threading import Event
import feedparser
import requests
import progressbar

DEFAULT_CHUNK_SIZE = 1024 * 100
DEFAULT_IGNORES_FILE = '.ignores'

LOG_FORMAT = '%(asctime)s %(process)d - %(levelname)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOGLEVEL = logging.ERROR

# Event for signalling.
shutdown = Event()

# Initate a global logger
logger = logging.getLogger(__name__)

# Triggers the shutdown event on receipt of a signal.
def shutdown_handler(x,y):
    shutdown.set()

# Register some signals with our shutdown handler.
signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGQUIT, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)


class PodcastBackup:

    def __init__(self, parser):

        opts = parser.parse_args()
        
        self.chunk_size = DEFAULT_CHUNK_SIZE
        self.feed = opts.feed
        self.output = opts.output
        self.type = opts.type

        self.matcher = None
        if opts.filter:
            try:
                self.matcher = re.compile('%s' % opts.filter, re.UNICODE)
            except Exception as e:
                print("Problem with filter:")
                print(e)

    def parseFeed(self):
        print("Parsing feed...")
        f = feedparser.parse(self.feed)

        podcasts = []
        for entry in f["entries"]:
            podcast = {}
            podcast["title"] = entry["title"]

            if "subtitle_detail" in entry:
                podcast["text"] = entry["subtitle_detail"]["value"]
            elif "subtitle" in entry:
                podcast["text"] = entry["subtitle"]
            else:
                print("Could not figure out description, skipping")

            if "links" in entry:
                links = []
                for item in entry["links"]:
                    parts = item["href"].split("?")
                    if len(parts) > 2:
                        raise Exception("Problem parsing link url (too many '?')")
                    link = parts.pop(0).strip()
                    if link.endswith(self.type):
                       links.append(link)
                if len(links):
                    podcast["href"] = links.pop(0)
                else:
                    raise Exception("Could not determine audio URL:\n", entry["links"])
            else:
                raise Exception("Could not determine audio URL")

            if self.matcher:
                if self.matcher.search(podcast["title"]):
                    podcasts.append(podcast)
            else:
                podcasts.append(podcast)

        return {
            "title": f["feed"]["title"],
            "podcasts": podcasts
        }


    def downloadDirectory(self, feed_title):

        if self.output:
            download_directory = self.output
        else:
            pattern = re.compile('[\W_]+', re.UNICODE)
            download_directory = "./%s" % pattern.sub('', feed_title).lower()

        # Create directory for podcast
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        return download_directory

    def ignoresList(self, download_directory, ignoresfile=DEFAULT_IGNORES_FILE):

        ignores = []
        ignores_file = os.path.join(download_directory, ignoresfile)
        if os.path.exists(ignores_file):
            try:
                # Horrible little parser
                with open(ignores_file, 'r') as f:
                    for line in f:
                        # ignore comments
                        if not line.startswith("#"):
                            raw = line.rstrip().split(":")
                            field = raw[0]
                            value = raw[1]
                            if len(raw) > 2:
                                value = ":".join(raw[1:])
                            ignores.append({field.strip(): value.strip()})
            except:
                raise Exception("Invalid ignores file.\n" \
                                "Should be one entry per line, title:foo bar baz")
        return ignores

    def run(self, chunk_size=DEFAULT_CHUNK_SIZE, ignoresfile=DEFAULT_IGNORES_FILE):

        feed = self.parseFeed()
        downloads = self.downloadDirectory(feed["title"])
        ignores = self.ignoresList(downloads, ignoresfile=ignoresfile)

        for podcast in feed["podcasts"]:
            if shutdown.is_set():
                print("Stopping...")
                break

            write_properties = 'wb'
            local_filename = os.path.join(downloads, podcast["href"].split('/')[-1])
            metadata_filename = "%s.metadata.json" % local_filename

            ignore = False
            for rule in ignores:
                for k, v in rule.items():
                    if k in podcast:
                        if podcast[k] == v:
                            ignore = True

            if ignore:
                print('Ignoring "%s" from %s file...' % (podcast["title"], ignores_file))
                continue

            print("Processing episode: %s" % podcast["title"])
            print("URL: %s" % podcast["href"])

            # Write some metadata alongside
            print("Writing metadata to %s" % metadata_filename)
            with open(metadata_filename, 'w') as f:
                json.dump(podcast, f, indent = 4)

            try:
                r = requests.get(podcast["href"], stream=True)
                if r.status_code > 400:
                    print("--- ERROR:")
                    print("--- Could not download this podast :( (Status %d)" % r.status_code)
                    print("---")
                    continue
            except requests.exceptions.RequestException as e:
                print("--- ERROR:")
                print(e)
                print("---")
                continue

            expected_size = 0
            if 'content-length' in r.headers:
                expected_size = int(r.headers['content-length'])

            progress = 0
            # Couldn't get a content-length from server
            if expected_size > 0:
                # Check whether already downloaded
                if os.path.isfile(local_filename):
                    size_on_disk = os.path.getsize(local_filename)
                    if size_on_disk == expected_size:
                        print("Already downloaded, skipping...")
                        continue
                    else:
                        print("%s downloaded, but mismatched file size (%d/%d)" % (local_filename, size_on_disk, expected_size))
                        r = requests.get(podcast["href"], stream=True, headers={'Range': 'bytes=%d-%d' % (size_on_disk, expected_size)})
                        if r.status_code == 206:
                            print("Resuming...")
                            write_properties = 'ab'
                            progress = size_on_disk
                        else:
                            print("Redownloading...")
                            os.remove(local_filename)

            if expected_size == 0:
                print("Warning: could not determine file size, no progress will be indicated.")

            print("Saving to: %s" % local_filename)
            bar = progressbar.ProgressBar(maxval=expected_size, \
                            widgets=[progressbar.Bar('#', '[', ']'), ' ',
                                    progressbar.Percentage(), ' ',
                                    progressbar.FileTransferSpeed()])

            with open(local_filename, write_properties) as f:
                for chunk in r.iter_content(chunk_size=self.chunk_size):
                    # check for shutdown
                    if shutdown.is_set():
                        print("Stopping...")
                        break
                    if chunk:
                        f.write(chunk)
                        # do progress
                        progress += self.chunk_size
                        if progress <= expected_size:
                            bar.update(progress)
                        if progress >= expected_size:
                            bar.finish()
        
def run():

    parser = argparse.ArgumentParser(description='Helps you back up your podcasts.')

    parser.add_argument('-f', '--feed', required=True,
                        help="RSS feed url")
    parser.add_argument('-o', '--output', default=None, required=False,
                        help="Location for downloaded items")
    parser.add_argument('-t', '--type', default='.mp3', required=False,
                        help="File extension to look for in feed items")
    parser.add_argument('-i', '--filter', default=None, required=False,
                        help="Apply a regular expression filter on titles")

    logging.basicConfig(level=LOGLEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT)
    try:
        pb = PodcastBackup(parser)
        pb.run()

    except Exception as e:
        print(e)
        exit(1)

