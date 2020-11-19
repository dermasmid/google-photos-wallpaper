# photos-wallpaper

Have photos from your google photos libary set as your wallpaper.

## Installation

``` bash
git clone https://github.com/dermasmid/google-photos-wallpaper
cd google-photos-wallpaper
sudo chmod +x setup.sh
./setup.sh -e
```

## Get Credentials

To allow a script to use Google Drive API we need to authenticate
our self towards Google.  To do so, we need to create a project,
describing the tool and generate credentials. Please use your web
browser and go to the [Google Developers Console](https://console.developers.google.com) and :

* Choose **"Create Project"** in popup menu on the top.

* A dialog box appears, so give your project a name and click on **"Create"** button.

* On the left-side menu click on **"API Manager"**.

* A table of available APIs is shown. Switch **"Drive API"** and click on **"Enable API"** button. Other APIs might be switched off, for our purpose.

* On the left-side menu click on **"Credentials"**.

* In section **"OAuth consent screen"** select your email address and give your product a name. Then click on **"Save"** button.

* In section **"Credentials"** click on **"Add credentials"** and switch **"OAuth 2.0 client ID"**.

* A dialog box  **"Create Cliend ID"** appears. Select **"Application type"** item as **"Other"**.

* Click on **"Create"** button.

* Click on **"Download JSON"** icon on the right side of created **"OAuth 2.0 client IDs"** and store the downloaded file on your file system. Please be aware, the file contains your private credentials, so take care of the file in the same way you care of your private SSH key; i.e. move downloaded JSON file to **google-photos-wallpaper**.

* Then, the first time you run it your browser window will open a google authorization request page. Approve authorization and then the credentials will work as expected.
