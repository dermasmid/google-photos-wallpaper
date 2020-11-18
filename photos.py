#!/usr/bin/python3
import google_workspace
import os
import requests
import time
import subprocess
import getpass
import pwd



ALBUM_ID = os.environ.get('ALBUM_ID')
SLEEP_MINS = int(os.environ.get('SLEEP_MINS'))
SAVE_PHOTOS = bool(os.environ.get('SAVE_PHOTOS'))
WALLPAPER_DIR = f'{os.getcwd()}/wallpapers'




scope = google_workspace.types.Scope('https://www.googleapis.com/auth/photoslibrary.readonly', '', '')
service = google_workspace.service.GoogleService('photoslibrary', scopes= [scope], version= 'v1')




def main():
    next_page_token = None
    most_recent_photo = []
    while True:

        # get the album from google photos
        album_data = service.mediaItems().search(body= {"albumId": ALBUM_ID, "pageToken": next_page_token}).execute()

        photos = album_data.get('mediaItems', [])
        for photo in photos:
            filename = photo.get('filename')
            file_path = f'{WALLPAPER_DIR}/{filename}'

            # if file is not on disk, download
            if not os.path.exists(file_path):
                download_photo(filename, photo.get('baseUrl'))
            
            # set as wallpaper
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file:///{file_path}'])

            # delete old photo if not save photos
            if not SAVE_PHOTOS:
                most_recent_photo.append(file_path)
                if len(most_recent_photo) > 1:
                    os.remove(most_recent_photo.pop(0))
            
            time.sleep(SLEEP_MINS * 60)
            

        next_page_token = album_data.get('nextPageToken')



def download_photo(filename: str, url: str):
    data = requests.get(f'{url}=w1000').content
    with open(f'{WALLPAPER_DIR}/{filename}', "wb") as f:
        f.write(data)





if __name__ == "__main__":
    main()
