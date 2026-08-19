#!/usr/bin/env bash
set -e
python3 -m pip install --upgrade pip
python3 -m pip install buildozer cython
buildozer -v android debug
mkdir -p dist
cp -f bin/*.apk dist/GNV_V28_26_debug.apk
printf '\nAPK gerado em: dist/GNV_V28_26_debug.apk\n'
