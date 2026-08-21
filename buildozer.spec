[app]

# ============================================================
# GNV V28.26 - SISTEMA DE CALCULO E ANALISE DE GNV
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
#
# IMPORTANTE:
# python3 e hostpython3 precisam ter EXATAMENTE a mesma
# versao durante o processo de compilacao.
#
# O projeto utiliza Python 3.12.9.
#
# ============================================================

requirements = python3==3.12.9,hostpython3==3.12.9,kivy,openpyxl,fpdf2,pillow

# ============================================================
# PYTHON-FOR-ANDROID
# ============================================================
#
# Utilizar a linha MASTER, compativel com Python 3.12.
#
# ============================================================

p4a.branch = master

# ============================================================
# ANDROID
# ============================================================

android.api = 35

android.minapi = 23

android.ndk = 27c

android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True

android.permissions = INTERNET

android.allow_backup = True

android.debug_artifact = apk

# ============================================================
# ORIENTACAO
# ============================================================

orientation = portrait

fullscreen = 0

# ============================================================
# ICONE
# ============================================================
#
# Caso exista icon.png de 512x512 na pasta do projeto,
# descomente a linha abaixo.
#
# icon.filename = %(source.dir)s/icon.png

# ============================================================
# PRESPLASH
# ============================================================
#
# Caso exista presplash.png, descomente:
#
# presplash.filename = %(source.dir)s/presplash.png


[buildozer]

# Nivel de log:
# 1 = normal
# 2 = detalhado
# 3 = muito detalhado

log_level = 2

warn_on_root = 1
