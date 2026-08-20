[app]
# GNV V28.26 — Android
# Aplicativo de cálculo e análise de capacidade de cilindro de GNV.
title = Sistema GNV V28.26
package.name = gnvcalculator
package.domain = br.com.gaiochristiano
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,csv,txt,kv
version = 28.26
requirements = python3,kivy,openpyxl,fpdf2,pillow,setuptools
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.permissions = INTERNET
android.allow_backup = True
android.debug_artifact = apk

# Ícone opcional: colocar icon.png 512x512 na raiz e descomentar.
# icon.filename = %(source.dir)s/icon.png

# Presplash opcional.
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1

