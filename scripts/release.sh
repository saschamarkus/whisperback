#!/bin/sh

set -e
set -u

OLDVERSION=$(/bin/grep "version=" setup.py | sed -E "s/^.*version='(.*)',/\1/g")
echo "Current version is $OLDVERSION. Please enter the new version"
read NEWVERSION

sed -i -E "s/version='$OLDVERSION',/version='$NEWVERSION',/g" setup.py

sed -i "3c $NEWVERSION" doc/whisperback.t2t

sed -i -E "s/__version__ = '$OLDVERSION'/__version__ = '$NEWVERSION'/g" whisperBack/gui.py

sed -i -E "s/Version=$OLDVERSION/Version=$NEWVERSION/g" data/whisperback.desktop

export DEBFULLNAME="Tails developers"
export DEBEMAIL="tails@boum.org"
gbp dch --auto --release --new-version="$NEWVERSION" --spawn-editor=always

git commit \
    setup.py \
    doc/whisperback.t2t \
    whisperBack/gui.py \
    data/whisperback.desktop \
    debian/changelog \
    -m "$(dpkg-parsechangelog -SSource) ($(dpkg-parsechangelog -SVersion))

Gbp-Dch: Ignore
"
git show

gbp buildpackage --git-tag-only --git-sign-tags
