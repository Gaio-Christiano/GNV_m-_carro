[app]

title = Sistema GNV V28.26

package.name = gnvcalculator

package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,json,csv,txt,kv

version = 28.26

requirements = python3==3.12.9,kivy,openpyxl,fpdf2,pillow

orientation = portrait

fullscreen = 0

android.api = 35

android.minapi = 23

android.ndk = 27c

android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True

android.permissions = INTERNET

android.allow_backup = True

android.debug_artifact = apk


[buildozer]

log_level = 2

warn_on_root = 1


