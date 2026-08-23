[app]

title = Sistema de Calculos e Analise da Capacidade do Cilindro de GNV - V28.27
package.name = gnvcalculator
package.domain = br.com.gaiochristiano
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,csv,txt,kv
source.exclude_dirs = .buildozer,bin,__pycache__,.git
version = 28.27
requirements = python3==3.12.9,hostpython3==3.12.9,kivy,openpyxl,pillow
p4a.branch = master
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 26
android.ndk = 28c
android.ndk_api = 26
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.permissions = INTERNET
android.allow_backup = True
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
