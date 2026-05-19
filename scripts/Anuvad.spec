# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


ROOT = Path(SPECPATH).parent

datas = [
    (str(ROOT / "app.cfg"), "."),
    (str(ROOT / "assets" / "icons"), "assets/icons"),
    (str(ROOT / "assets" / "images" / "icon.ico"), "assets/images"),
    (str(ROOT / "assets" / "i18n"), "assets/i18n"),
    (str(ROOT / "assets" / "qss"), "assets/qss"),
]
datas += collect_data_files("indic_transliteration")

excludes = [
    "PIL",
    "Pillow",
    "PyQt5.QtBluetooth",
    "PyQt5.QtCharts",
    "PyQt5.QtDataVisualization",
    "PyQt5.QtDesigner",
    "PyQt5.QtHelp",
    "PyQt5.QtLocation",
    "PyQt5.QtMultimedia",
    "PyQt5.QtMultimediaWidgets",
    "PyQt5.QtNetworkAuth",
    "PyQt5.QtPositioning",
    "PyQt5.QtQml",
    "PyQt5.QtQuick",
    "PyQt5.QtQuickWidgets",
    "PyQt5.QtRemoteObjects",
    "PyQt5.QtSensors",
    "PyQt5.QtSerialPort",
    "PyQt5.QtSql",
    "PyQt5.QtTest",
    "PyQt5.QtWebChannel",
    "PyQt5.QtWebEngine",
    "PyQt5.QtWebEngineCore",
    "PyQt5.QtWebEngineWidgets",
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
    "PyQt5/Qt5/bin/Qt5Qml.dll",
    "PyQt5/Qt5/bin/Qt5QmlModels.dll",
    "PyQt5/Qt5/bin/Qt5Quick.dll",
    "PyQt5/Qt5/plugins/platforms/qminimal.dll",
    "PyQt5/Qt5/plugins/platforms/qoffscreen.dll",
    "PyQt5/Qt5/translations/*"
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
