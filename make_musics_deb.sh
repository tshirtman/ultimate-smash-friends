#!/usr/bin/env sh
# This script is part of ultimate-smash-friends
# this script build a debian/ubuntu package for ultimate-smash-friends

rm -r \
packaging/deb/musics/usr/share/games/ultimate-smash-friends/usf_media/musics/*
cp -r code/usf_media/musics \
packaging/deb/musics/usr/share/games/ultimate-smash-friends/usf_media/

dpkg -b packaging/deb/musics ultimate-smash-friends-musics_$(date +%Y-%m-%d).deb
rm -r \
packaging/deb/musics/usr/share/games/ultimate-smash-friends/usf_media/musics/*
