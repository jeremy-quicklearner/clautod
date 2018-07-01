#!/bin/bash
# Script for releasing clautod
# Given a version number, this script creates a debian package
# from the clautod source, adds it to the local repo, and tags
# the current git commit with the same version number. This is
# the clautod release flow.
# The script is almost certainly broken on all machines except
# my home PC where it's intended to be run. Don't try it!

# Check parameters
if [ ! $1 ] ; then
    echo "[release] Specify version string in X.X.X format"
    exit 1
fi
if [[ ! $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] ; then
    echo "[release] Version string <"$1"> is invalid. Use X.X.X format"
    exit 1
fi

echo "[release] Releasing clautod v"$1"..."
echo "[release] Preparing package tree..."

# Populate README files in debian directory
cp README.md debian/README.debian
cp README.md debian/README.source

# Populate changelog based on git log
echo "clautod ("$1") unstable; urgency=medium"                           > debian/changelog
echo ""                                                                 >> debian/changelog
git log --oneline $(git tag | sort -V | tail -n 1)..@ | sed 's/^/  * /' >> debian/changelog
echo ""                                                                 >> debian/changelog
echo " -- Jeremy Lerner <jeremy.cpsc.questions@gmail.com>  "$(date -R)  >> debian/changelog

# Let the user edit the changelist
nano debian/changelog

echo "[release] Package tree ready. Building package..."

# Build the Debian package
if ! dpkg-buildpackage -us -uc ; then
	echo "[release] Failed to build Debian package"
	exit 1
fi

# Tag the current commit in git
echo "[release] Package built. Tagging current commit as v"$1
if ! git tag -a v$1 && git push --tags ; then
    echo "[release] Failed to tag commit. This is not a legitimate release!"
    exit 1
fi

echo "[release] Commit tagged. Publishing to local repo..."

# Add the new package to the local repo
sudo reprepro -b /var/www/repos/apt/debian includedeb stretch ../clautod_$1_all.deb

echo "[release] Package published. Cleaning up..."

# Cleanup
rm ../clautod_$1_all.deb
rm ../clautod_$1_amd64.buildinfo
rm ../clautod_$1_amd64.changes
rm ../clautod_$1.dsc
rm ../clautod_$1.tar.xz

echo "[release] Cleaned up."
echo "[release] clautod v"$1" is published."
