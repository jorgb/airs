#!/bin/bash

cd ..

# delete all the python compiled files, and backup files
find -name "*.pyc" -exec rm '{}' \;
find -name "*.*~" -exec rm '{}' \;
find -name "*.bak" -exec rm '{}' \;

# delete old build
rm -rf build
mkdir build

rm -rf setup/build-ubuntu

cp airs.py build
cp airs.ico build
cp -r gui build
cp -r data build
cp -r doc build
cp setup/ubuntu/airs build
cp setup/ubuntu/airs-icon.png build
cp setup/ubuntu/airs.desktop build

cd build 
tar -czf ../deb.tar.gz *

cd ..
rm -rf build

mkdir build

cd build
mkdir airs-1.1
cd airs-1.1

mv ../../deb.tar.gz .
tar -zxf deb.tar.gz

dh_make -s -n -e jorgb@xs4all.nl -c GPL -f deb.tar.gz

rm debian/*.EX
rm debian/*.ex
rm debian/README
rm debian/README.Debian

cp -f ../../setup/ubuntu/changelog debian
cp -f ../../setup/ubuntu/compat debian
cp -f ../../setup/ubuntu/control debian
cp -f ../../setup/ubuntu/copyright debian
cp -f ../../setup/ubuntu/dirs debian
cp -f ../../setup/ubuntu/docs debian
cp -f ../../setup/ubuntu/rules debian

sudo dpkg-buildpackage -d

cd ..

mkdir -p ../setup/build-ubuntu
mv -f *.deb ../setup/build-ubuntu
mv -f *.dsc ../setup/build-ubuntu
mv -f *.changes ../setup/build-ubuntu

cd ..

sudo rm -rf build

bzr export airs.tar.gz 
mv airs.tar.gz setup/build-ubuntu
