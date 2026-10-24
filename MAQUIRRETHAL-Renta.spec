# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")
geo_datas, geo_binaries, geo_hiddenimports = collect_all("geocoder")

a = Analysis(
    ["MAQUIRRENTHAL -INVENTARIO.py"],
    pathex=[],
    binaries=ctk_binaries + geo_binaries,
    datas=(
        ctk_datas
        + geo_datas
        + [("assets/empresa_banner.png", "assets")]
    ),
    hiddenimports=ctk_hiddenimports + geo_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MAQUIRRETHAL Renta",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MAQUIRRETHAL Renta",
)
