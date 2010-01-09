mkdir tmp/
cd tmp/
unzip ../doc/ultimate-smash-friends.zip
cd ..
cp code tmp/ultimate-smash-friends/usr/share/games/ -R
mv tmp/ultimate-smash-friends/usr/share/games/code tmp/ultimate-smash-friends/usr/share/games/ultimate-smash-friends
cd tmp
dpkg -b ultimate-smash-friends/ ../ultimate-smash-friends.deb
cd ..
rm tmp/ -R
