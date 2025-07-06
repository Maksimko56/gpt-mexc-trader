[app]
title = GPT MEXC Trader
package.name = gptmexctrader
package.domain = org.example
source.dir = .
source.include_exts = py,kv
version = 1.0

requirements = python3,kivy,requests,pyjnius

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.archs = arm64-v8a

android.minapi = 21
android.api = 31
android.sdk = 33.0.2
android.ndk = 25b
android.ndk_api = 21
android.bootstrap = sdl2
android.allow_backup = 1
android.accept_sdk_license = True
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
android.sdk_path = $HOME/.buildozer/android/platform/android-sdk
android.ndk_path = $HOME/.buildozer/android/platform/android-ndk-r25b
