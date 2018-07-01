#!/bin/bash

# This script ensures the Clauto database is up-to-date.
# It should be run from the clautod postinst script on
# installation of clautod.

echo "[dbmig] HELLO I AM DBMIG"

# If the database directory doesn't exist, create it
#if [ ! -d /etc/clauto/clautod ]; then
#    echo "[dbmig] Database directory not found. Creating."
#    mkdir -p /etc/clauto/clautod/db
#fi

# If the database doesn't exist, create it