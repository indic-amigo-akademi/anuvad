# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


ROOT = Path(SPECPATH).parent

datas = [
    (str(ROOT / "app.cfg"), "."),
    (str(ROOT / "assets" / "icons"), "assets/icons"),
    (str(ROOT / "assets" / "fonts"), "assets/fonts"),
    (str(ROOT / "assets" / "images" / "icon.ico"), "assets/images"),
    (str(ROOT / "assets" / "i18n"), "assets/i18n"),
    (str(ROOT / "assets" / "qss"), "assets/qss"),
]
datas += collect_data_files("indic_transliteration")

excludes = [
    "PIL",
    "Pillow",
    "PyQt6.QtBluetooth",
    "PyQt6.QtCharts",
    "PyQt6.QtDataVisualization",
    "PyQt6.QtDesigner",
    "PyQt6.QtHelp",
    "PyQt6.QtLocation",
    "PyQt6.QtMultimedia",
    "PyQt6.QtMultimediaWidgets",
    "PyQt6.QtNetworkAuth",
    "PyQt6.QtPositioning",
    "PyQt6.QtQml",
    "PyQt6.QtQuick",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtRemoteObjects",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSql",
    "PyQt6.QtTest",
    "PyQt6.QtWebChannel",
    "PyQt6.QtWebEngine",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebEngineWidgets",
    "beautifulsoup4",
    "doc",
    "flake8",
    "htmlcov",
    "pycodestyle",
    "pyflakes",
    "pytest",
    "pytest-cov",
    "soupsieve",
    "tests",
    "unittest",
    "unused_locale",
]

excluded_binaries = (
    "PyQt6/Qt6/bin/Qt6Qml.dll",
    "PyQt6/Qt6/bin/Qt6QmlModels.dll",
    "PyQt6/Qt6/bin/Qt6Quick.dll",
    "PyQt6/Qt6/plugins/platforms/qminimal.dll",
    "PyQt6/Qt6/plugins/platforms/qoffscreen.dll",
    "PyQt6/Qt6/translations/*"
)


def keep_binary(entry):
    destination = entry[0].replace("\\", "/")
    return not any(Path(destination).match(pattern) for pattern in excluded_binaries)


a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=["indic_transliteration"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
a.binaries = [entry for entry in a.binaries if keep_binary(entry)]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Anuvad",
    # exclude_binaries=True,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(ROOT / "assets" / "images" / "icon.ico")],
)
# coll = COLLECT(
#     exe,
#     a.scripts,
#     a.binaries,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name="Anuvad",
# )
