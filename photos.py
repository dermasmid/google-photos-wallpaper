#!/usr/bin/python3
import google_workspace
import os
import requests
import subprocess
import json
import signal
from threading import Event


ALBUM_ID = os.environ.get("ALBUM_ID")
SLEEP_MINS = int(os.environ.get("SLEEP_MINS"))
SAVE_PHOTOS = bool(os.environ.get("SAVE_PHOTOS"))
WALLPAPER_DIR = f"{os.getcwd()}/wallpapers"


service = google_workspace.service.GoogleService(
    "photoslibrary",
    "wallpaper",
    scopes="https://www.googleapis.com/auth/photoslibrary.readonly",
    version="v1",
)

service.local_oauth()


def main(last_photo: str = None):
    stopper = GracefulStop()
    next_page_token = None
    most_recent_photo = []
    while True:

        # get the album from google photos
        album_data = (
            service.mediaItems()
            .search(body={"albumId": ALBUM_ID, "pageToken": next_page_token})
            .execute()
        )

        photos = album_data.get("mediaItems", [])
        for photo in photos:
            photo_id = photo.get("id")
            if not last_photo:
                file_path = f"{WALLPAPER_DIR}/{photo_id}"

                # if file is not on disk, download
                if not os.path.exists(file_path):
                    download_photo(photo_id, photo.get("baseUrl"))

                # set as wallpaper
                subprocess.run(
                    [
                        "gsettings",
                        "set",
                        "org.gnome.desktop.background",
                        "picture-uri",
                        f"file:///{file_path}",
                    ]
                )

                # delete old photo if not save photos
                if not SAVE_PHOTOS:
                    most_recent_photo.append(file_path)
                    if len(most_recent_photo) > 1:
                        os.remove(most_recent_photo.pop(0))

                stopper.exit.wait(SLEEP_MINS * 60)

                # Handle Stop
                if stopper.exit.is_set():
                    break

            else:
                if last_photo == photo_id:
                    last_photo = None
                    most_recent_photo.append(f"{WALLPAPER_DIR}/{photo_id}")

        next_page_token = album_data.get("nextPageToken")

        # Handle Stop
        if stopper.exit.is_set():
            with open("state.json", "w") as f:
                json.dump({"last_photo": photo_id}, f)
            break


def download_photo(photo_id: str, url: str):
    data = requests.get(f"{url}=w1500-h1000").content
    with open(f"{WALLPAPER_DIR}/{photo_id}", "wb") as f:
        f.write(data)


class GracefulStop:
    def __init__(self):
        self.exit = Event()
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGTERM, self.quit)

    def quit(self, signum, frame):
        self.exit.set()


if __name__ == "__main__":
    with open("state.json", "r") as f:
        state_data = json.load(f)
    if state_data:
        last_photo = state_data["last_photo"]
    else:
        last_photo = None
    main(last_photo=last_photo)
