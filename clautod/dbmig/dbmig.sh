#!/bin/bash

# This script ensures the Clauto database is up-to-date.
# It should be run from the clautod postinst script on
# installation of clautod.

DB_SCRIPTS_DIR=/usr/share/clauto/clautod/dbmig
CFG_FILE=/etc/clauto/clautod/clautod.cfg
CFG_KEY_DB_DIR=db_dir

# First, determine the database's location by reading the config file. Filter out the line with the database's location
db_dir=$(cat ${CFG_FILE} | egrep ^\\s*${CFG_KEY_DB_DIR}\\s*=.*$)

# Trim off the key and '=' character
db_dir=$(echo ${db_dir} | sed -r -e 's/.*=\s*//g')

# Trim off any trailing whitespace or comment
db_dir=$(echo ${db_dir} | sed -r -e 's/\s*(#.*)?//g')

# Now the absolute path of the database is known
db_file=${db_dir}/clauto.db
db_file_backup=${db_dir}/clauto.db.bak

# If the database doesn't exist, create it with USER_VERSION 0
if [ ! -f ${db_file} ] ; then
    echo "[dbmig] Clauto database not found. Creating empty database."
    touch ${db_file}
    sqlite3 ${db_file} < ${DB_SCRIPTS_DIR}/0.sql
fi

# Determine what version the existing database is at
DB_VERSION_CURRENT=$(sqlite3 ${db_file} 'PRAGMA user_version')

# Determine what version the database should be
DB_VERSION_GOAL=$(cat ${DB_SCRIPTS_DIR}/dbversion.txt)

# Make a backup of the database in case something goes wrong
cp ${db_file} ${db_file_backup}

# Apply each script in order until the goal version is reached
echo -n "[dbmig] Migrating Clauto database to version(s) <0>..."
while [ ${DB_VERSION_CURRENT} -ne ${DB_VERSION_GOAL} ] ; do
    # Determine the next database version
    DB_VERSION_NEXT=0
	let DB_VERSION_NEXT=${DB_VERSION_CURRENT}+1

    # Ensure a migration script exists for that version
    if [ ! -f ${DB_SCRIPTS_DIR}/${DB_VERSION_NEXT}.sql ] ; then
        echo ; >&2 echo "[dbmig] Error: Migration script for database version <"${DB_VERSION_NEXT}"> not found. Unable to migrate to version <"${DB_VERSION_GOAL}">"
        >&2 echo "Clauto Database migration failed"
        mv ${db_file_backup} ${db_file}
        exit 1
    fi

    # Apply the migration script
    echo -n "<"${DB_VERSION_NEXT}">..."
    sqlite3 ${db_file} < ${DB_SCRIPTS_DIR}/${DB_VERSION_NEXT}.sql

    # Ensure the migration script updated the user_version pragma
    if [ $(sqlite3 ${db_file} 'PRAGMA user_version') -ne ${DB_VERSION_NEXT} ] ; then
        echo ; >&2 echo "[dbmig] Error: Migration script for database version <"${DB_VERSION_NEXT}"> didn't update user_version pragma. Unable to migrate to version <"${DB_VERSION_GOAL}">"
         >&2 echo "Clauto Database migration failed"
         mv ${db_file_backup} ${db_file}
        exit 1
    fi

    # Update the current version
    DB_VERSION_CURRENT=$(sqlite3 ${db_file} 'PRAGMA user_version')
done

# Migration is complete
echo ; echo "[dbmig] Clauto database is up-to-date at version <"${DB_VERSION_CURRENT}">"
rm ${db_file_backup}
exit 0