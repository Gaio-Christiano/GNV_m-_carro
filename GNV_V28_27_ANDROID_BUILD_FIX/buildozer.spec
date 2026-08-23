[app]

# ============================================================
# GNV V28.27 - ANDROID
# ============================================================

title = Sistema GNV V28.27

package.name = gnvcalculator

package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,csv,txt

version = 28.27

# ============================================================
# DEPENDENCIAS
# ============================================================
#
# IMPORTANTE:
# Neste primeiro APK usamos somente Kivy.
#
# openpyxl / fpdf2 / pillow foram retirados do build Android
# para eliminar as dependencias que estavam provocando falhas
# no cross-compiling.
#
requirements = python3==3.12.9,hostpython3==3.12.9,kivy

# ============================================================
# INTERFACE
# ============================================================

orientation = portrait

fullscreen = 0

# ============================================================
# ANDROID
# ============================================================

android.api = 35

android.minapi = 23

android.ndk = 28c

android.archs = arm64-v8a

android.accept_sdk_license = True

android.permissions = INTERNET

android.allow_backup = True

android.debug_artifact = apk

# ============================================================
# ICON
# ============================================================

# Coloque icon.png na mesma pasta do buildozer.spec
# caso queira utilizar um icone personalizado.

# icon.filename = %(source.dir)s/icon.png

# ============================================================
# PRESPLASH
# ============================================================

# presplash.filename = %(source.dir)s/presplash.png


[buildozer]

log_level = 2

warn_on_root = 1
