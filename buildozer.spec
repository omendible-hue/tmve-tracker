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
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.build_tools_version = 30.0.3
android.archs = arm64-v8a
android.allow_backup = True
fullscreen = 0
 
[buildozer]
log_level = 2
warn_on_root = 1
