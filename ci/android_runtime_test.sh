#!/usr/bin/env bash
set -euo pipefail

PACKAGE="br.com.gaiochristiano.gnvcalculator"
WORKSPACE="${GITHUB_WORKSPACE:-$(pwd)}"
APK_DIR="${WORKSPACE}/apk"
RUNTIME_LOG="${WORKSPACE}/android_runtime.log"
PACKAGE_DUMP="${WORKSPACE}/package_dump.txt"
ACTIVITY_DUMP="${WORKSPACE}/activity_dump.txt"

mkdir -p "${APK_DIR}"

APK="$(find "${APK_DIR}" -type f -name '*x86_64*.apk' -print -quit || true)"
if [[ -z "${APK}" ]]; then
  APK="$(find "${APK_DIR}" -type f -name '*.apk' -print -quit || true)"
fi

if [[ -z "${APK}" ]]; then
  echo "ERRO: nenhum APK foi encontrado em ${APK_DIR}" >&2
  find "${APK_DIR}" -maxdepth 5 -type f -print >&2 || true
  exit 1
fi

echo "APK selecionado: ${APK}"
echo "Tamanho: $(stat -c '%s' "${APK}") bytes"

adb devices -l
adb wait-for-device
adb install -r "${APK}"
adb shell pm clear "${PACKAGE}" >/dev/null 2>&1 || true
adb logcat -c

collect_diagnostics() {
  adb logcat -d -v time > "${RUNTIME_LOG}" || true
  adb shell dumpsys package "${PACKAGE}" > "${PACKAGE_DUMP}" || true
  adb shell dumpsys activity activities > "${ACTIVITY_DUMP}" || true
}
trap collect_diagnostics EXIT

echo "=== INICIANDO APLICATIVO ==="
adb shell monkey -p "${PACKAGE}" 1

# O app é o APK real e não deve ser encerrado automaticamente.
# O teste verifica se o processo sobrevive ao tempo de inicialização e se
# não existem sinais conhecidos de crash no logcat.
sleep 5

echo "=== PROCESSO APÓS 5s ==="
PID="$(adb shell pidof "${PACKAGE}" 2>/dev/null | tr -d '\r' || true)"
echo "PID=${PID}"

if [[ -z "${PID}" ]]; then
  echo "FAIL: aplicativo encerrou antes de 5s" >&2
  echo "=== LOGCAT DE FALHA ===" >&2
  adb logcat -d -v time | tail -800 >&2 || true
  exit 1
fi

sleep 10

echo "=== PROCESSO APÓS 15s ==="
PID="$(adb shell pidof "${PACKAGE}" 2>/dev/null | tr -d '\r' || true)"
echo "PID=${PID}"

LOGTMP="$(mktemp)"
adb logcat -d -v time > "${LOGTMP}" || true

if grep -qEi 'Fatal Python|init_fs_encoding|failed to get the Python codec|No module named .encodings.|FATAL EXCEPTION|Fatal signal|SIGSEGV|SIGABRT|UnsatisfiedLinkError|ImportError|ModuleNotFoundError|Traceback|dlopen failed' "${LOGTMP}"; then
  echo "FAIL: encontrado erro fatal de runtime no logcat" >&2
  grep -nEi 'Fatal Python|init_fs_encoding|failed to get the Python codec|No module named .encodings.|FATAL EXCEPTION|Fatal signal|SIGSEGV|SIGABRT|UnsatisfiedLinkError|ImportError|ModuleNotFoundError|Traceback|dlopen failed' "${LOGTMP}" >&2 || true
  exit 1
fi

if [[ -z "${PID}" ]]; then
  echo "FAIL: aplicativo morreu entre 5s e 15s" >&2
  echo "=== LOGCAT DE FALHA ===" >&2
  tail -1000 "${LOGTMP}" >&2 || true
  exit 1
fi

echo "PASS: aplicativo permanece em execução após 15s; PID=${PID}"
echo "=== LOGCAT PYTHON/KIVY ==="
grep -nEi 'python|kivy|sdl|main.py|GNV' "${LOGTMP}" | tail -250 || true
rm -f "${LOGTMP}"
