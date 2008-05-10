#!/bin/bash

# delete all the python compiled files, and backup files
find -name "*.pyc" -exec rm '{}' \;
find -name "*.*~" -exec rm '{}' \;
find -name "*.bak" -exec rm '{}' \;

# delete old build
rm -rf build
mkdir build

cp airs.py build
cp airs.ico build
cp -r gui build
cp -r data build
cp -r doc build

cd build 
tar -czf ../deb.tar.gz *

cd ..
rm -rf build

mkdir build

cd build
mkdir airs-1.0
cd airs-1.0

mv ../../deb.tar.gz .
tar -zxf deb.tar.gz

dh_make -s -n -e jorgb@xs4all.nl -c GPL -f deb.tar.gz

rm debian/*.EX
rm debian/*.ex
rm debian/README
rm debian/README.Debian

cp ../../setup/ubuntu/* debian

sudo dpkg-buildpackage -d

cd ..

mv -f *.deb ../setup
mv -f *.dsc ../setup
mv -f *.changes ../setup

cd ..

sudo rm -rf build
