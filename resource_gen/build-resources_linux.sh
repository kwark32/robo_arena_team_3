#!/bin/sh
python3 ./qrcgen.py ../sounds/ /
#pyrcc5 ./.qrc -o ../resources.py
rm ../resources.rcc
rcc -binary -no-compress ./.qrc -o ../resources.rcc
rm ./.qrc
