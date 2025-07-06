[app]
title = GPT MEXC Trader
package.name = gptmexctrader
package.domain = org.example
source.dir = .
source.include_exts = py,kv
version = 1.0

# Без openai!
requirements = python3,kivy,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
