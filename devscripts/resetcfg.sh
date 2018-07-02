#!/bin/bash

# This script resets the config of the local
# clautod instance, as if it was just installed
# for the first time

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[resetcfg] clautod not installed"
    exit 1
fi

# Bring down the clautod instance
echo "[resetcfg] Stopping clautod..."
sudo systemctl stop clautod

# Delete the config
echo "[resetcfg] clautod stopped. Deleting config..."
sudo rm -f /etc/clauto/clautod/clautod.cfg

# Enact config migration to rebuild the config
echo "[resetcfg] Config deleted. Enacting config migration..."
sudo /usr/share/clauto/clautod/cfgmig/cfgmig.sh

# Bring up the clautod instance
echo "[resetcfg] Config migration complete. Starting clautod..."
sudo systemctl start clautod

echo "[resetcfg] clautod started."
echo "[resetcfg] State reset."