[app]

# ============================================================
# SISTEMA GNV V28.26 - ANDROID
# ============================================================

title = Sistema de Calculos e Analise da Capacidade do Cilindro de GNV - V28.26

package.name = gnvcalculator

package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,json,csv,txt,kv

source.exclude_dirs = .buildozer,bin,__pycache__,.git

version = 28.26

# ============================================================
# PYTHON
# ============================================================

requirements = python3==3.12.9,hostpython3==3.12.9,kivy,openpyxl,fpdf2,pillow

# ============================================================
# PYTHON-FOR-ANDROID
# ============================================================

p4a.branch = master

# ============================================================
# ANDROID
# ============================================================

android.api = 35

android.minapi = 26

android.ndk = 28c

android.ndk_api = 26

android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True

android.permissions = INTERNET

android.allow_backup = True

android.debug_artifact = apk

# ============================================================
# INTERFACE
# ============================================================

orientation = portrait

fullscreen = 0

# ============================================================
# ICONE
# ============================================================

# Caso tenha icon.png de 512x512:
#
# icon.filename = %(source.dir)s/icon.png

# ============================================================
# PRESPLASH
# ============================================================

# Caso tenha presplash.png:
#
# presplash.filename = %(source.dir)s/presplash.png


[buildozer]

log_level = 2

warn_on_root = 1
