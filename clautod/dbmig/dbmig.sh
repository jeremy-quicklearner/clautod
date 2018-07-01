#!/bin/bash

# This script ensures the Clauto database is up-to-date.
# It should be run from the clautod postinst script on
# installation of clautod.

DB_FILE=/etc/clauto/clautod/clauto.db
DB_SCRIPTS_DIR=/usr/share/clauto/clautod/dbmig

# If the database doesn't exist, create it with USER_VERSION 0
if [ ! -f $DB_FILE ] ; then
    echo "[dbmig] Clauto database not found. Creating empty database."
    touch $DB_FILE
    sqlite3 $DB_FILE < $DB_SCRIPTS_DIR/0.sql
fi

# Determine what version the existing database is at
DB_VERSION_CURRENT=$(sqlite3 $DB_FILE 'PRAGMA user_version')

# Determine what version the database should be
DB_VERSION_GOAL=$(cat $DB_SCRIPTS_DIR/dbversion.txt)


# Apply each script in order until the goal version is reached
echo -n "[dbmig] Migrating Clauto database to version(s) "
while [ $DB_VERSION_CURRENT -ne $DB_VERSION_GOAL ] ; do
    # Determine the next database version
	let DB_VERSION_NEXT=$DB_VERSION_CURRENT+1

    # Ensure a migration script exists for that version
    if [ ! -f $DB_SCRIPTS_DIR/$DB_VERSION_NEXT.sql ] ; then
        echo ; >&2 echo "[dbmig] Error: Migration script for database version <"$DB_VERSION_NEXT"> not found. Unable to migrate to version <"$DB_VERSION_GOAL">"
        >&2 echo "Clauto Database migration failed"
        exit 1
    fi

    # Apply the migration script
    echo -n $DB_VERSION_NEXT"..."
    sqlite3 $DB_FILE < $DB_SCRIPTS_DIR/$DB_VERSION_NEXT.sql

    # Ensure the migration script updated the user_version pragma
    if [ $(sqlite3 $DB_FILE 'PRAGMA user_version') -ne $DB_VERSION_NEXT ] ; then
        echo ; >&2 echo "[dbmig] Error: Migration script for database version <"$DB_VERSION_NEXT"> didn't update user_version pragma. Unable to migrate to version <"$DB_VERSION_GOAL">"
         >&2 echo "Clauto Database migration failed"
        exit 1
    fi

    # Update the current version
    DB_VERSION_CURRENT=$(sqlite3 $DB_FILE 'PRAGMA user_version')
done

# Migration is complete
echo ; echo "[dbmig] Clauto database is up-to-date at version <"$DB_VERSION_CURRENT">"
exit 0