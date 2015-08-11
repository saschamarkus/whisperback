#!/bin/sh

OLDVERSION=$(/bin/grep "version=" setup.py | sed -E "s/^.*version='(.*)',/\1/g")
echo "Current version is $OLDVERSION. Please enter the new version"
read NEWVERSION

sed -i -E "s/version='$OLDVERSION',/version='$NEWVERSION',/g" setup.py

sed -i "3c $NEWVERSION" doc/whisperback.t2t

sed -i -E "s/__version__ = '$OLDVERSION'/__version__ = '$NEWVERSION'/g" whisperBack/gui.py

sed -i -E "s/Version=$OLDVERSION/Version=$NEWVERSION/g" data/whisperback.desktop

sed -i "\$a \\\n$NEWVERSION\n$(echo $NEWVERSION | tr '[:graph:]' '=')\n" ChangeLog
#echo "Please edit ChangeLog…"
editor ChangeLog

#echo "Please edit Debian changelog…"
export DEBFULLNAME="Tails developers"
export DEBEMAIL="tails@boum.org"
dch --newversion $NEWVERSION

#git ci -m "Update version to $NEWVERSION" setup.py doc/whisperback.t2t whisperback/whisperback.py data/whisperback.desktop ChangeLog debian/changelog
