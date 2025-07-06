[app]
title = GPT MEXC Trader
package.name = gptmexctrader
package.domain = org.example
source.dir = .
source.include_exts = py,kv
version = 1.0

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.archs = arm64-v8a

# 🔧 ОБЯЗАТЕЛЬНО: указать API, NDK и Build Tools
android.minapi = 21
android.api = 31
android.sdk = 33.0.2
android.ndk = 25b
android.ndk_api = 21

# 🔧 Удаляет предупреждение об отсутствии файла icon.png
icon.filename = %(source.dir)s/icon.png

# 🔧 Поддержка текущих Android-сборок
android.allow_backup = 1

# 🔧 Разрешить сборку в GitHub Actions или WSL без GUI
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
