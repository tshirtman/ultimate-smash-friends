#!/usr/bin/env sh
# This script is part of ultimate-smash-friends
# this script build a debian/ubuntu package for ultimate-smash-friends

rm -rf packaging/deb/medias/usr/share/games/ultimate-smash-friends/*
cp -r code/usf_media/ packaging/deb/medias/usr/share/games/ultimate-smash-friends/
rm -r packaging/deb/medias/usr/share/games/ultimate-smash-friends/usf_media/musics
dpkg -b packaging/deb/medias ultimate-smash-friends-medias_$(date +%Y-%m-%d).deb
rm -r packaging/deb/medias/usr/share/games/ultimate-smash-friends/*
