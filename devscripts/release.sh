#!/bin/bash

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

echo "[release] Commit tagged. Publishing to local Debian repo..."

# Add the new package to the local repo
sudo reprepro -b /var/www/repos/apt/debian includedeb stretch ../clautod_$1_all.deb

# Move all the build artefacts to the clauto-releases repo
echo "[release] Package published. Moving artefacts to clauto-releases Git repo"

mkdir -p ../clauto-releases/clautod_$1
mv ../clautod_$1_all.deb         ../clauto-releases/clautod_$1
mv ../clautod_$1_amd64.buildinfo ../clauto-releases/clautod_$1
mv ../clautod_$1_amd64.changes   ../clauto-releases/clautod_$1
mv ../clautod_$1.dsc             ../clauto-releases/clautod_$1
mv ../clautod_$1.tar.xz          ../clauto-releases/clautod_$1

# Commit and push to clauto-releases
echo "[release] Artefacts moved. Committing and pushing..."

cd ../clauto-releases/clautod_$1
git add .
git status
git commit -m "Released clautod_"$1
git push origin master

echo "[release] Committed and pushed."
echo "[release] clautod_"$1" is live."
