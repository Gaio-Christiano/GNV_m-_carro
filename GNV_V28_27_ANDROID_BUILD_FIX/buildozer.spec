[app]

title = Sistema de Calculos e Analise da Capacidade do Cilindro de GNV - V28.46
package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv
source.exclude_dirs = .buildozer,bin,__pycache__,tests,p4a
version = 28.46

# Python 3.11: python3 e hostpython3 precisam ser EXATAMENTE a mesma versao.
# fpdf2 foi retirado dos requirements Android porque o resolvedor do
# python-for-android nao consegue resolver suas dependencias para a plataforma
# Android e abortava a compilacao antes de gerar um APK novo.
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,filetype==1.2.0,openpyxl,pillow

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
