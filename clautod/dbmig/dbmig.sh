#!/bin/bash

# This script ensures the Clauto database is up-to-date.
# It should be run from the clautod postinst script on
# installation of clautod.

DB_FILE=/etc/clauto/clautod/clauto.db

# If the database doesn't exist, create it with USER_VERSION 0
if [ ! -f $DB_FILE ] ; then
    echo "[dbmig] Clauto database not found. Creating empty database."
    touch $DB_FILE
    sqlite3 $DB_FILE < 0.sql
fi

# Determine what version the existing database is at
DB_VERSION_CURRENT=$(sqlite3 $DB_FILE 'PRAGMA user_version')

# Determine what version the database should be
DB_VERSION_GOAL=$(cat dbversion.txt)