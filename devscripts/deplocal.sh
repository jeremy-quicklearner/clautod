#!/bin/bash

# This script copies the clautod source in the repo
# into clautod's read installation directory where
# it replaces the local instance of clautod. It's a
# way of testing new code without doing a release

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[deplocal] clautod not installed"
    exit 1
fi

# Bring down the clautod instance
sudo systemctl stop clautod

# Copy the clautod source from the repo to the clautod installation directory
sudo cp -r clautod/* /usr/share/clauto/clautod

# There may have been config changes, so enact config migration
if ! sudo /usr/share/clauto/clauto-common/sh/cfgmig.sh clautod ; then
    echo "[deplocal] Config migration failure detected. Exiting without restarting clautod"
    exit 1
fi

# There may have been database changes, so enact database migration
if ! sudo /usr/share/clauto/clautod/dbmig/dbmig.sh ; then
    echo "[deplocal] DB migration failure detected. Exiting without restarting clautod"
    exit 1
fi

# Bring up the clautod instance
sudo systemctl start clautod