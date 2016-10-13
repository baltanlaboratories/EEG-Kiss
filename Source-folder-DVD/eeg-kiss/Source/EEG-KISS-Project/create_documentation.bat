#!/bin/bash
cp source/conf.py tmp
rm -r source
rm -r build
sphinx-apidoc -d 2 --full --force -H eeg-kiss -A Fourtress -V 1 -R 1 -o source "."
mv tmp source/conf.py
sphinx-build -b singlehtml source build 