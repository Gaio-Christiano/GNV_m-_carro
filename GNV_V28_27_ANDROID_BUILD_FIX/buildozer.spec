[app]

title = Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV - V28.37

package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv

source.exclude_dirs = .buildozer,bin,__pycache__,tests,p4a

version = 28.37

# Dependências Android.
# O sistema principal ainda usa openpyxl e fpdf2 nas funções de exportação.
# O bootstrap V28.37 impede que essas funções sejam acionadas durante a subida
# inicial e carrega as abas somente quando o usuário as seleciona.
requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1,filetype==1.2.0,openpyxl,pillow,fpdf2

orientation = portrait

fullscreen = 0

android.api = 35
android.minapi = 26
android.ndk = 28c
android.ndk_api = 26
android.accept_sdk_license = True
android.allow_backup = True

# SQLite/configuracoes usam o armazenamento privado do proprio aplicativo.
# INTERNET permanece para as funcoes que usam recursos de rede.
android.permissions = INTERNET

android.debug_artifact = apk

p4a.source_dir = p4a

[buildozer]
log_level = 2
warn_on_root = 1
