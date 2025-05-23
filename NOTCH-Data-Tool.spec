# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['notch_data_tool.py'],
    pathex=[],
    binaries=[],
    datas=[('readme.md', '.'), ('modules/*.py', 'modules'), ('weather.csv', '.')],
    hiddenimports=['modules.app', 'modules.config', 'modules.midi', 'modules.weather_tab', 'modules.settings_tab', 'modules.midi_tab'],
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
    a.binaries,
    a.datas,
    [],
    name='NOTCH-Data-Tool',
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
    icon=['weather.ico'],
)
