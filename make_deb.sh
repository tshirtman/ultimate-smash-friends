#!/usr/bin/env sh
# This script is part of ultimate-smash-friends
# this script build a debian/ubuntu package for ultimate-smash-friends

mkdir tmp/
unzip doc/ultimate-smash-friends.zip -d tmp
cp code tmp/ultimate-smash-friends/usr/share/games/ -R
rm tmp/ultimate-smash-friends/usr/share/games/usf_modules/
rm -r tmp/ultimate-smash-friends/usr/share/games/code/usf_media/musics/mp3/
mv tmp/ultimate-smash-friends/usr/share/games/code tmp/ultimate-smash-friends/usr/share/games/ultimate-smash-friends
dpkg -b tmp/ultimate-smash-friends/ ultimate-smash-friends.deb
rm tmp/ -R
