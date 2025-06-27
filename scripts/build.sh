#!/usr/bin/env bash
set -e
pyinstaller --onefile -n ble-gui qt_frontend/__main__.py
pyinstaller --onefile -n ble-scan cli/main.py
pyinstaller --onefile -n ble-web api/__main__.py
case "$(uname)" in
Linux*)
    # Build AppImage
    if command -v appimagetool >/dev/null; then
        appimagetool dist/ble-gui dist/ble-gui.AppImage
    fi
    ;;
Darwin*)
    mkdir -p dist/ble-gui.app/Contents/MacOS
    cp dist/ble-gui dist/ble-gui.app/Contents/MacOS/
    ;;
esac
