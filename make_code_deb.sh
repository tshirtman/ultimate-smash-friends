#!/usr/bin/env sh
# This script is part of ultimate-smash-friends
# this script build a debian/ubuntu package for ultimate-smash-friends

rm -rf packaging/deb/code/usr/share/games/ultimate-smash-friends/*
cp -r code/ultimate-smash-friends\
      code/usf_modules/\
      code/default_config.cfg\
      code/default_keys.cfg\
      code/default_sound.cfg\
      code/sequences.cfg\
      code/ultimate-smash-friends.pot\
      code/viewer\
      packaging/deb/code/usr/share/games/ultimate-smash-friends/

dpkg -b packaging/deb/code ultimate-smash-friends-code_$(date +%Y-%m-%d).deb
rm -r packaging/deb/code/usr/share/games/ultimate-smash-friends/*
