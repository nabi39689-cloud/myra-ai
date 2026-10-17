[app]
title = Myra AI
package.name = myraai
package.domain = org.myra
source.dir = .
source.include_exts = py,png,jpg,xml
version = 0.1
requirements = python3,kivy==2.3.0,flask,werkzeug,jinja2,markupsafe,itsdangerous,click,blinker
orientation = portrait
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.ndk = 25b
android.ndk_api = 24
p4a.branch = v2024.01.21
p4a.branch = v2024.01.21
p4a.branch = v2024.01.21
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.extra_manifest_application_arguments = extra_app_args.xml

[buildozer]
log_level = 2
warn_on_root = 1
