import os
import re
import time
import httpx
import random
from bs4 import BeautifulSoup

absolute_path = os.path.dirname(__file__)
headers = {}


def to_filename(title: str) -> str:
    # standardise filenames and remove dangerous characters
    cleaned = re.sub("[\'\"!@#$%^*(),.?/]", "", title.strip().lower())
    cleaned = re.sub("&", "and", cleaned)
    return re.sub("[\s]", "_", cleaned)


def clean_lyrics(raw: str) -> str:
    # standardise lyrics
    return re.sub("\r", "", raw.strip())


def scrape():
    # compilation of song lyrics
    base_url = "https://geniuslyrics.net/red-hot-chili-peppers/timeline/"
    root_page = httpx.get(base_url, headers=headers).text
    soup = BeautifulSoup(root_page, "html.parser")

    # albums are arranged in reverse-chronological order
    album_index = 10
    for album in soup.find_all("div", class_="albums-list"):
        # skip songs without albums
        if album_index == 0:
            album_index = 14

        album_title = album.strong.text
        album_folder = to_filename(album_title)

        print(f"Saving <{album_title}> ...\n")
        album_path = f"{absolute_path}/{album_index:02}_{album_folder}"

        # create the album directory if it doesn't exist
        try:
            os.mkdir(album_path)
        except:
            pass

        # select all anchor tags
        songs = [li.a for li in album.find_all("li")]
        for index, song in enumerate(songs):
            song_name = song.attrs["title"]
            song_href = song.attrs["href"]
            song_page = httpx.get(song_href, headers=headers).text

            mini_soup = BeautifulSoup(song_page, "html.parser")
            song_title = mini_soup.find("h2", class_="title")
            song_body = song_title.find_next_siblings("p")
            lyrics = (paragraph.get_text("\n") for paragraph in song_body)
            lyrics = clean_lyrics("\n\n".join(lyrics))

            song_index = index + 1
            song_path = f"{album_path}/{song_index:02}_{to_filename(song_name)}.txt"
            with open(song_path, "w", encoding="utf-8") as song:
                song.write(f"{song_name}\n\n")
                song.write(lyrics)

            print(f"{song_index:02}. {song_name}")
            time.sleep(2 + random.random() * 10)

        album_index -= 1
        print()
