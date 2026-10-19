[app]
title = JARVIS
package.name = jarvis
package.domain = org.jarvis
source.dir = .
source.include_exts = py,ttf,png
version = 0.1
requirements = python3,kivy,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
