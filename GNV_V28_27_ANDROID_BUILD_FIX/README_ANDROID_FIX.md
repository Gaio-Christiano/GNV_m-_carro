# GNV V28.27 — Android build fix

## Causa real identificada no log

1. `fpdf2` entra no auto module resolution do python-for-android e o pip para a plataforma Android não consegue resolver as versões do pacote.
2. O `pip install -U pip` interno do p4a atualiza de 24.3.1 para 26.2.1 e o venv fica inconsistente, produzindo `open_rich_spinner`/API interna do pip.

## Correção

- `fpdf2` foi retirado dos requirements Android.
- O import de FPDF virou opcional. O PDF continua disponível no Windows/desktop; no Android o botão informa a limitação em vez de derrubar o aplicativo.
- `openpyxl` é mantido.
- Antes do build, o workflow baixa o python-for-android e aplica um patch local para usar `pip<26.2` no venv interno.

## Arquivos

- `main.py`: V28.27 para Android.
- `buildozer.spec`: Python 3.12.9, Kivy, openpyxl, Pillow.
- `.github/workflows/android.yml`: build automático.
