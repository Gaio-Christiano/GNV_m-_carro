# Correção V28.27

Substitua o workflow V28.27 por `.github/workflows/android.yml` deste pacote.

Pontos corrigidos:
- Python 3.12.9 EXATO no runner.
- `python3` e `hostpython3` EXATAMENTE 3.12.9.
- NDK 28c.
- Java 17 com setup-java v5.
- Não chama `sdkmanager` global inexistente.
- `log_level = 2`.
- Log completo salvo em `build_full.log`.
- Diagnóstico e logs são publicados mesmo quando o build falha.
- APK só é publicado se realmente existir.

Não crie manualmente a pasta `p4a`. O Buildozer/p4a cria sua própria estrutura em `.buildozer`.

Se `main.py` não existir dentro de `GNV_V28_27_ANDROID_BUILD_FIX`, o workflow copia automaticamente o primeiro `.py` encontrado nessa pasta.
