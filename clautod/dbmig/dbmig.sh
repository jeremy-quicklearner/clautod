#!/bin/bash

# This script ensures the Clauto database is up-to-date.
# It should be run from the clautod postinst script on
# installation of clautod.

echo "[dbmig] HELLO I AM DBMIG"

# If the database doesn't exist, create it