[app]
title = Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV
package.name = gnvcalculator
package.domain = org.gaiocristiano
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,db,sqlite3,txt,ttf,otf
version = 28.27
requirements = python3==3.12.9,hostpython3==3.12.9,kivy,openpyxl,fpdf2,pillow,pyjnius
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 23
android.ndk = 28c
android.ndk_api = 23
android.archs = arm64-v8a
android.accept_sdk_license = True
android.copy_libs = 1
p4a.branch = master
log_level = 2
source.exclude_dirs = .buildozer,bin,venv,__pycache__,tests
source.exclude_exts = pyc,pyo,log

[buildozer]
warn_on_root = 0
