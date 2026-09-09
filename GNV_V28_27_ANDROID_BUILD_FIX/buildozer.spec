[app]

title = Sistema de Calculos e Analise da Capacidade do Cilindro de GNV - V28.45
package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv
source.exclude_dirs = .buildozer,bin,__pycache__,tests,p4a
version = 28.45

# Python 3.11 e usado deliberadamente nesta build. O runtime anterior com
# Python 3.12 chegou a carregar libpython3.12.so, mas abortou antes de executar
# main.py com "failed to get the Python codec of the filesystem encoding".
# Python-for-android tem suporte consolidado a 3.11 desde a release 2024.01.21.
requirements = python3==3.11.9,kivy==2.3.1,filetype==1.2.0,openpyxl,pillow,fpdf2

orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 26
android.ndk = 28c
android.ndk_api = 26
android.accept_sdk_license = True
android.allow_backup = True
android.permissions = INTERNET
android.archs = arm64-v8a,x86_64
android.debug_artifact = apk
p4a.source_dir = p4a

[buildozer]
log_level = 2
warn_on_root = 1
