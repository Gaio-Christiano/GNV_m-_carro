[app]

title = Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV - V28.27

package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv

source.exclude_dirs = .buildozer,bin,__pycache__,tests,p4a

version = 28.27

# Kivy 2.3.1 usa o pacote filetype em tempo de execução.
# Sem ele o APK pode compilar normalmente e fechar imediatamente ao iniciar.
requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1,filetype==1.2.0,openpyxl,pillow

orientation = portrait

fullscreen = 0

android.api = 35

android.minapi = 26

android.ndk = 28c

android.ndk_api = 26

android.accept_sdk_license = True

android.allow_backup = True

android.permissions = INTERNET

android.debug_artifact = apk

# Usa a cópia local do python-for-android preparada e corrigida pelo workflow.
p4a.source_dir = p4a

[buildozer]

log_level = 2

warn_on_root = 1
