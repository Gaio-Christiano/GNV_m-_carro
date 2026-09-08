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
sleep 5

echo "=== PROCESSO APÓS 5s ==="
PID="$(adb shell pidof "${PACKAGE}" 2>/dev/null | tr -d '\r' || true)"
echo "PID=${PID}"

if [[ -z "${PID}" ]]; then
  echo "APLICATIVO ENCERRADO DURANTE A INICIALIZAÇÃO" >&2
  echo "=== LOGCAT IMEDIATO ===" >&2
  adb logcat -d -v time | tail -300 >&2 || true
  exit 1
fi

sleep 20

echo "=== PROCESSO APÓS 25s ==="
PID="$(adb shell pidof "${PACKAGE}" 2>/dev/null | tr -d '\r' || true)"
echo "PID=${PID}"

if [[ -z "${PID}" ]]; then
  echo "APLICATIVO ENCERRADO ANTES DE 25s" >&2
  echo "=== LOGCAT IMEDIATO ===" >&2
  adb logcat -d -v time | tail -500 >&2 || true
  exit 1
fi

echo "APLICATIVO PERMANECEU EXECUTANDO POR 25s"
