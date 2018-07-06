#!/bin/bash

# This script resets the state of the local
# clautod instance, as if it was just installed
# for the first time

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[resetstate] clautod not installed"
    exit 1
fi

# Bring down the clautod instance
echo "[resetstate] Stopping clautod..."
sudo systemctl stop clautod

# Delete the database and config
echo "[resetstate] clautod stopped. Deleting database..."
sudo rm -f /etc/clauto/clautod/clauto.db
echo "[resetstate] Database deleted. Deleting config..."
sudo rm -f /etc/clauto/clautod/clautod.cfg

# Enact config migration to rebuild the config
echo "[resetstate] Config deleted. Enacting config migration..."
sudo /usr/share/clauto/clauto-common/sh/cfgmig.sh clautod

# Enact database migration to rebuild the database
echo "[resetstate] Config migration complete. Enacting database migration..."
sudo /usr/share/clauto/clautod/dbmig/dbmig.sh

# Bring up the clautod instance
echo "[resetstate] Database migration complete. Starting clautod..."
sudo systemctl start clautod

echo "[resetstate] clautod started."
echo "[resetstate] State reset."