#!/bin/sh


# Check if pip3 is installed
PIP_CMD=$(command -v pip3)

# If pip is not installed suggest to install and exit.
if [ -z "$PIP_CMD" ]; then
    echo "pip3 not installed. Please run sudo apt -y install python3-pip and re-run script"
    exit 1
fi



# Set additional flags for installation options
while getopts hd:s:ept: option; do 
    case $option in
        h) echo "The following options are available:
           -d specify taget installation. (default is /usr/local/bin)
           -s specify syslog application
           -e enable and start service after installation
           -h this help menu
           -p save photos
           -t time to change wallpaper"
           exit 0
        ;;
        d) INSTALL_DIR=${OPTARG}
        ;;
        s) SYSLOG_CMD=${OPTARG}
        ;;
        e) ENABLED=1
        ;;
        p) SAVE_PHOTOS=1
        ;;
        t) SLEEP_MINS=${OPTARG}
        ;;
        *) echo "invalid option"
           exit 0
        ;;
    esac
done


# If -t was not specified default to 5
if [ -z "$SLEEP_MINS" ]; then
    echo "Sleep time not specified, defaulting to 5"
    SLEEP_MINS=5
fi


# If -d was not specified, install in /usr/local/bin
if [ -z "$INSTALL_DIR" ]; then
    echo "No install directory specified, defaulting to /usr/local/bin"
    INSTALL_DIR=/usr/local/bin;
fi

# Create INSTALL_DIR if it does not exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "$INSTALL_DIR does not exist. creating"
    mkdir -p "$INSTALL_DIR"
fi


WORK_DIR=~/.config/photos_wallpaper;

WALLPAPER_DIR=$WORK_DIR/wallpapers;


# Create WALLPAPER_DIR if it does not exist
if [ ! -d "$WALLPAPER_DIR" ]; then
    echo "$WALLPAPER_DIR does not exist. creating"
    mkdir -p "$WALLPAPER_DIR"
fi


# clean the file
> enviroment.env

echo "SLEEP_MINS=$SLEEP_MINS" >> enviroment.env
echo "SAVE_PHOTOS=$SAVE_PHOTOS" >> enviroment.env


# If -s flag was not set, automatically check what syslog is being used.
RSYSLOG_PID=$(pgrep rsyslog)
SYSLOG_NG=$(pgrep syslog-ng)

if [ -z "$SYSLOG_CMD" ]; then
    if [ -z "$RSYSLOG_PID" ]; then
    SYSLOG_CMD=syslog-ng;
    SYSLOG_CONF=etc/syslog-ng/conf.d/0gphotos.conf
    else
        if [ -z "$SYSLOG_NG" ]; then
        SYSLOG_CMD=rsyslog;
        SYSLOG_CONF=etc/rsyslog.d/photos_wallpaper.conf;
        fi
    fi
fi


# Install requirements
$PIP_CMD install -r requirements.txt > /dev/null

echo "Running select_album"
sudo chmod +x select_album.py
./select_album.py


cp *.pickle $WORK_DIR
cp enviroment.env $WORK_DIR



# Generate unit file based on variables set.
echo "Generating systemd unit file"
cat << EOF > ~/.config/systemd/user/photos_wallpaper.service
[Unit]
Description=Google photos wallpaper


[Service]
Type=simple
WorkingDirectory=$WORK_DIR
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=$WORK_DIR/enviroment.env
ExecStart=$INSTALL_DIR/photos.py
SyslogIdentifier=photos_wallpaper
SyslogFacility=local7
SyslogLevel=info

[Install]
WantedBy=multi-user.target
EOF


# Configure syslog
echo "configuring syslog"
sudo cp $SYSLOG_CONF /$SYSLOG_CONF


# Install photos_wallpaper
echo "Installing photos_wallpaper to $INSTALL_DIR"
sudo cp photos.py $INSTALL_DIR
sudo chmod +x $INSTALL_DIR/photos.py


# reload systemd and syslog
echo "reloading systemd"
sudo systemctl daemon-reload
sudo systemctl restart $SYSLOG_CMD.service
sudo systemctl restart systemd-journald


# Enable and start if -e flag was set. 
if [ "$ENABLED" = 1 ]; then
    echo "Enabling and starting service"
    systemctl --user enable photos_wallpaper.service;
    systemctl --user start photos_wallpaper.service;
fi
