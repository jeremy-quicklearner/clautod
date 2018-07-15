#!/bin/bash

# This script copies the clautod source in the repo
# into clautod's read installation directory where
# it replaces the local instance of clautod, and also
# resets the local instance's state

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[depreslocal] clautod not installed"
    exit 1
fi

# Bring down the clautod instance
sudo systemctl stop clautod

# Run the deplocal script for the clauto_common module
cd ../clauto-common
./devscripts/deplocal.sh
cd ../clautod

# Copy the clautod source from the repo to the clautod installation directory
sudo cp -r clautod/* /usr/share/clauto/clautod

# Reset the local instance's state
./devscripts/resetstate.sh

# Bring up the clautod instance
sudo systemctl start clautod