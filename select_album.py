#!/usr/bin/python3
import google_workspace
import os


scope = google_workspace.types.Scope(
    "https://www.googleapis.com/auth/photoslibrary.readonly", "", ""
)
service = google_workspace.service.GoogleService(
    "photoslibrary", scopes=[scope], version="v1"
)


def main():
    albums_dict = {}
    index = 0
    next_page_token = None
    done = False
    while not done:
        albums_data = (
            service.albums().list(pageSize=50, pageToken=next_page_token).execute()
        )
        albums = albums_data.get("albums")
        for album in albums:
            albums_dict[str(index)] = {
                "title": album.get("title"),
                "id": album.get("id"),
                "url": album.get("productUrl"),
            }
            index += 1
        next_page_token = albums_data.get("nextPageToken")

        if not next_page_token:
            done = True

    for album_index in albums_dict:
        print(
            f'{album_index}: {albums_dict[album_index]["title"]}    ({albums_dict[album_index]["url"]})'
        )
    selected_album_index = input("Please enter the number of the album you want: ")

    if not selected_album_index in albums_dict:
        raise ValueError("invalid selection!!")

    print(f'You selected: {albums_dict[selected_album_index]["title"]}')
    with open("enviroment.env", "a") as e:
        e.write(f'ALBUM_ID={albums_dict[selected_album_index]["id"]}')


if __name__ == "__main__":
    main()
