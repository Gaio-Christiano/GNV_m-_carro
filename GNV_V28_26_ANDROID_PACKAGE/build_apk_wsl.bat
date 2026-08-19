@echo off
setlocal
cd /d "%~dp0"
echo ================================================
echo GNV V28.26 - BUILD ANDROID VIA WSL
echo ================================================
echo.
echo Este script chama o Ubuntu/WSL e executa build_apk.sh.
echo Na primeira compilacao o Buildozer baixara SDK/NDK e pode demorar.
echo.
wsl bash -lc "cd '$(wslpath '%~dp0')' && chmod +x build_apk.sh && ./build_apk.sh"
if errorlevel 1 (
  echo.
  echo ERRO durante a compilacao.
  pause
  exit /b 1
)
echo.
echo APK pronto na pasta dist.
pause
