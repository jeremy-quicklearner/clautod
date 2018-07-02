#!/bin/bash

# This script resets the local Clauto database,
# as if clautod was just installed
# for the first time

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[resetdb] clautod not installed"
    exit 1
fi

# Bring down the clautod instance
echo "[resetdb] Stopping clautod..."
sudo systemctl stop clautod

# Delete the database
echo "[resetdb] clautod stopped. Deleting database..."
sudo rm -f /etc/clauto/clautod/clauto.db

# Enact database migration to rebuild the database
echo "[resetdb] Database deleted. Enacting database migration..."
sudo /usr/share/clauto/clautod/dbmig/dbmig.sh

# Bring up the clautod instance
echo "[resetdb] Database migration complete. Starting clautod..."
sudo systemctl start clautod

echo "[resetdb] clautod started."
echo "[resetdb] Database reset."