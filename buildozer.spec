[app]
title = TMVE Tracker
package.name = tmvetracker
package.domain = org.tmve
source.dir = .
source.include_exts = py,json
version = 1.0
requirements = python3,kivy==2.3.0,plyer,pyjnius
orientation = portrait
android.permissions = ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
fullscreen = 0
android.presplash_color = #1565C0

[buildozer]
log_level = 2
warn_on_root = 1
