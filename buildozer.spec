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

# API, NDK, Build Tools
android.minapi = 21
android.api = 31
android.sdk = 33.0.2
android.ndk = 25b
android.ndk_api = 21

# Поддержка иконки
icon.filename = %(source.dir)s/icon.png

# Разрешить сборку в CI и WSL
android.allow_backup = 1
android.accept_sdk_license = True

# ⛔ Убираем deprecated настройку
# android.bootstrap = sdl2  ← не используем!

# ✅ Используем актуальное имя
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1

# Указываем точные пути к SDK/NDK, чтобы не было ошибок
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
android.accept_sdk_license = True