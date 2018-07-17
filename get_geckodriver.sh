#! /bin/sh
VERSION="0.21.0"
FILENAME="geckodriver-v$VERSION-linux64.tar.gz"
wget https://github.com/mozilla/geckodriver/releases/download/v$VERSION/$FILENAME
tar -xvzf $FILENAME
rm $FILENAME
