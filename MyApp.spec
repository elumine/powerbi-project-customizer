# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.datastruct import Tree

ui_resources = Tree("src/ui", prefix="ui", excludes=["__pycache__", "*.py", "*.pyc"])
feature_qml_resources = Tree("src/features", prefix="features", excludes=["__pycache__", "*.py", "*.pyc"])

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    # ``Tree`` returns PyInstaller TOC triples, while Analysis(datas=...) only
    # accepts source/destination pairs. Add the QML trees after Analysis.
    datas=[("content", "content")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
a.datas += ui_resources + feature_qml_resources
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Project1",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)