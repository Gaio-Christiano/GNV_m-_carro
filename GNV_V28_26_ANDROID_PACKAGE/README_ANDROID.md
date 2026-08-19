# GNV V28.26 — Pacote Android

## O que é
Este pacote contém a versão V28.26 do Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV, preparada para compilação como APK Android.

A versão usa Kivy para a interface móvel e mantém as funções de cálculo, histórico SQLite, configurações, exportação e compartilhamento presentes no código-fonte.

## Arquivo principal
`main.py` — código-fonte da aplicação.

## Dependências Android
- Python 3
- Kivy
- openpyxl
- fpdf2
- Pillow

## APK de teste (debug)
O comando de compilação é:

    buildozer -v android debug

O APK será criado em `bin/`.

## Windows 10/11
O Buildozer não executa nativamente no Windows; a documentação oficial do Kivy recomenda Linux/macOS e informa que Windows pode usar WSL. Portanto, no Windows, instale WSL2 com Ubuntu e execute:

    cd /mnt/c/caminho/para/GNV_V28_26_ANDROID_PACKAGE
    chmod +x build_apk.sh
    ./build_apk.sh

Também existe `build_apk_wsl.bat` para iniciar o processo a partir do Windows.

## GitHub Actions
O diretório `.github/workflows/android.yml` permite compilar o APK no GitHub Actions sem instalar o Android SDK/NDK no computador Windows.

Após colocar o conteúdo do pacote em um repositório GitHub, abra Actions → `Build APK Android - GNV V28.26` → `Run workflow`. Ao terminar, o APK ficará disponível como artefato `GNV-V28.26-APK`.

## Instalação no Redmi Note 9 Pro
O build inclui `arm64-v8a` e `armeabi-v7a`, portanto foi preparado para o Redmi Note 9 Pro e para ampla compatibilidade com aparelhos Android compatíveis. A compatibilidade final depende da versão do Android e das bibliotecas disponíveis no dispositivo.

No aparelho:
1. Transfira o APK.
2. Abra o arquivo.
3. Autorize a instalação de aplicativo proveniente do gerenciador de arquivos, se o Android solicitar.
4. Instale.
5. Abra `Sistema GNV V28.26`.

## Atenção sobre o cálculo
O programa é uma ferramenta analítica/estimativa. O volume físico do cilindro não deve ser confundido com volume equivalente de referência. O código utiliza um fator Z informado pelo usuário como aproximação; não é uma implementação AGA8/GERG nem um instrumento metrológico oficial.
