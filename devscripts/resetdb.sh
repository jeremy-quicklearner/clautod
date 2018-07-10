#!/bin/bash

# This script resets the local Clauto database,
# as if clautod was just installed
# for the first time

CFG_FILE=/etc/clauto/clautod/clautod.cfg
CFG_KEY_DB_DIR=db_dir

# Ensure clautod is installed
if [ "$(dpkg-query -W --showformat='${Status}\n' clautod | grep 'install ok installed')" == "" ] ; then
    echo "[resetdb] clautod not installed"
    exit 1
fi

# This code for determining the database's absolute path is duplicated from dbmig.sh,
# but shouldn't be refactored into its own script because devscripts shouldn't share code with the package
# Determine the database's location by reading the config file. Filter out the line with the database's location
db_dir=$(cat ${CFG_FILE} | egrep ^\\s*${CFG_KEY_DB_DIR}\\s*=.*$)

# Trim off the key and '=' character
db_dir=$(echo ${db_dir} | sed -r -e 's/.*=\s*//g')

# Trim off any trailing whitespace or comment
db_dir=$(echo ${db_dir} | sed -r -e 's/\s*(#.*)?//g')

# Now the absolute path of the database is known
db_file=${db_dir}/clauto.db

# Bring down the clautod instance
echo "[resetdb] Stopping clautod..."
sudo systemctl stop clautod

# Delete the database
echo "[resetdb] clautod stopped. Deleting database..."
sudo rm -f ${db_file}

# Enact database migration to rebuild the database
echo "[resetdb] Database deleted. Enacting database migration..."
sudo /usr/share/clauto/clautod/dbmig/dbmig.sh

# Bring up the clautod instance
echo "[resetdb] Database migration complete. Starting clautod..."
sudo systemctl start clautod

echo "[resetdb] clautod started."
echo "[resetdb] Database reset."