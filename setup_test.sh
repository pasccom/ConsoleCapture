#!/bin/sh
# Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
#
# This file is part of ConsoleCapture.
#
# ConsoleCapture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ConsoleCapture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ConsoleCapture. If not, see <http://www.gnu.org/licenses/>

# Absolute path to folder containing script (and related files):
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"
SCRIPT_DIR="$PWD"
cd - > /dev/null

# Delete old test environment:
ANS=
if [ -d "$SCRIPT_DIR/env" ]; then
    echo "Folder $SCRIPT_DIR/env already exists. Do you want to delete it (y/N)?"
    while true; do
        read ANS
        if [ -z "$ANS" -o "$ANS" == 'n' -o "$ANS" == 'N' ]; then
            echo "OK, skipping"
            ANS='skip'
            break
        fi
        if [ "$ANS" == 'y' -o "$ANS" == 'Y' ]; then
            rm -R "$SCRIPT_DIR/env"
            ANS=
            break
        fi
    done
fi

# Create test environment:
if [ -z "$ANS" ]; then
    virtualenv --system-site-packages "$SCRIPT_DIR/env"
    . "$SCRIPT_DIR/env/bin/activate"
    pip install --upgrade pip
    pip install selenium
    deactivate
fi

# Get and install Gecko driver:
if [ -z "$ANS" ]; then
    if [ -f "$SCRIPT_DIR/gecko-version.local" ]; then
        GECKO_VERSION=$(cat "$SCRIPT_DIR/gecko-version.local")
    else
        GECKO_VERSION=$(curl "https://github.com/mozilla/geckodriver/releases/latest" | sed -e 's|^<html><body>You are being <a href="https://github.com/mozilla/geckodriver/releases/tag/\(v[0-9]\+.[0-9]\+.[0-9]\+\)">redirected</a>.</body></html>$|\1|')
    fi
    case $(uname -m) in
        x86)
            GECKO_NAME="geckodriver-$GECKO_VERSION-linux32.tar.gz"
            ;;
        x86_64)
            GECKO_NAME="geckodriver-$GECKO_VERSION-linux64.tar.gz"
            ;;
        arm*)
            GECKO_NAME="geckodriver-$GECKO_VERSION-arm7hf.tar.gz"
            ;;
    esac
    rm "$GECKO_NAME" 2> /dev/null
    wget "https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/$GECKO_NAME"
    tar -xzf "$GECKO_NAME"
    mv geckodriver "$SCRIPT_DIR/env/bin"
    rm "$GECKO_NAME"
fi
