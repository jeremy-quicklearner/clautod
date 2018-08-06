#!/bin/bash

# This script copies the clautod source in the repo
# into clautod's read installation directory where
# it replaces the local instance of clautod. It's a
# way of testing new code without doing a release

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[clautod deplocal] clautod not installed"
    exit 1
fi

# Build clauto-web
cd clautod/clauto-web
npm run build
if [ $? -ne 0 ] ; then
    echo "[clautod deplocal] Web build failed. Not deploying."
    exit 1
fi
cd ../..

# Bring down the clautod instance
sudo systemctl stop clautod

# Run the deplocal script for the clauto_common module
cd ../clauto-common
./devscripts/deplocal.sh
cd ../clautod

# Copy the clautod source from the repo to the clautod installation directory
sudo cp -r clautod/cfgmig /usr/share/clauto/clautod
sudo cp -r clautod/dbmig /usr/share/clauto/clautod
sudo cp -r clautod/entities /usr/share/clauto/clautod
sudo cp -r clautod/layers /usr/share/clauto/clautod
sudo cp -r clautod/server /usr/share/clauto/clautod
sudo cp -r clautod/web /usr/share/clauto/clautod
sudo cp clautod/clautod.py /usr/share/clauto/clautod

# There may have been config changes, so enact config migration
if ! sudo /usr/share/clauto/clauto-common/sh/cfgmig.sh clautod ; then
    echo "[clautod deplocal] Config migration failure detected. Exiting without restarting clautod"
    exit 1
fi

# There may have been database changes, so enact database migration
if ! sudo /usr/share/clauto/clautod/dbmig/dbmig.sh ; then
    echo "[clautod deplocal] DB migration failure detected. Exiting without restarting clautod"
    exit 1
fi

# Bring up the clautod instance
sudo systemctl start clautod
