[app]

title = Sistema GNV V28.27

package.name = gnvcalculator
package.domain = br.com.gaiochristiano

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,txt,csv

version = 28.27

requirements = python3==3.12.9,kivy

orientation = portrait

fullscreen = 0

android.api = 35

android.minapi = 23

android.ndk = 28c

android.archs = arm64-v8a

android.accept_sdk_license = True

android.permissions = INTERNET

android.allow_backup = True

android.debug_artifact = apk

android.debug_symbols = 1

p4a.branch = v2024.01.21


[buildozer]

log_level = 2

warn_on_root = 1
