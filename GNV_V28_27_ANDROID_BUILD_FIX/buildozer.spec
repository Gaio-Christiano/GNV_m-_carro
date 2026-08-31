[app]

title = Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV - V28.36

package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv

source.exclude_dirs = .buildozer,bin,__pycache__,tests,p4a

version = 28.36

# Dependências do aplicativo Android.
# fpdf2 permanece no APK porque o sistema gera relatórios PDF, mas o
# bootstrap main.py agora impede que fpdf2 seja importado durante o startup.
# A biblioteca só é carregada quando o código realmente instancia FPDF.
requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1,filetype==1.2.0,openpyxl,pillow,fpdf2

orientation = portrait

fullscreen = 0

android.api = 35

android.minapi = 26

android.ndk = 28c

android.ndk_api = 26

android.accept_sdk_license = True

android.allow_backup = True

# O banco SQLite e os arquivos de configuração ficam no armazenamento
# privado do próprio aplicativo. Não é necessário READ/WRITE_EXTERNAL_STORAGE
# para esse armazenamento privado.
android.permissions = INTERNET

android.debug_artifact = apk

# Usa a cópia local do python-for-android preparada e corrigida pelo workflow.
p4a.source_dir = p4a

[buildozer]

log_level = 2

warn_on_root = 1
