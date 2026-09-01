[app]
title = GNV Android Smoke Test
package.name = gnvsmoketest
package.domain = br.com.gaiochristiano
source.dir = .
source.include_exts = py
source.exclude_dirs = .buildozer,bin,__pycache__,p4a
version = 1.1
requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1
p4a.source_dir = p4a
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 26
android.ndk = 28c
android.ndk_api = 26
android.accept_sdk_license = True
android.allow_backup = False
android.permissions = INTERNET
android.debug_artifact = apk
[buildozer]
log_level = 2
warn_on_root = 1
