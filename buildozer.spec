[app]
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
android.presplash_color = #0a0f2c
title = Myra AI
package.name = myraai
package.domain = org.myra
source.dir = .
source.include_exts = py,png,jpg,xml
version = 0.1
requirements = python3,flask,werkzeug==2.2.3,jinja2,markupsafe,itsdangerous,click,blinker
orientation = portrait
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.ndk = 25b
android.ndk_api = 24
p4a.branch = v2024.01.21
p4a.bootstrap = webview
p4a.port = 5000
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.extra_manifest_application_arguments = extra_app_args.xml

[buildozer]
log_level = 2
warn_on_root = 1
