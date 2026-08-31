[app]

title = Sistema de Calculos e Analise da Capacidade do Cilindro de GNV - V28.39
package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv
source.exclude_dirs = .buildozer,bin,__pycache__,tests,p4a
version = 28.39

requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1,filetype==1.2.0,openpyxl,pillow,fpdf2

orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 26
android.ndk = 28c
android.ndk_api = 26
android.accept_sdk_license = True
android.allow_backup = True

# Nesta versao testamos explicitamente a hipotese de armazenamento externo.
# O armazenamento privado continua sendo usado para o SQLite do sistema.
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.debug_artifact = apk
p4a.source_dir = p4a

[buildozer]
log_level = 2
warn_on_root = 1
