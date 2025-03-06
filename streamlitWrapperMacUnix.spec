# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [("lessdrf-desktop/lib/python3.12/site-packages/streamlit/runtime", "./streamlit/runtime")]
datas += [("lessdrf-desktop/lib/python3.12/site-packages/streamlit/static", "./streamlit/static")]
datas += [("lessdrf-desktop/lib/python3.12/site-packages/st_aggrid/frontend", "./st_aggrid/frontend")]
datas += [("lessdrf-desktop/lib/python3.12/site-packages/streamlit_tree_select/frontend", "./streamlit_tree_select/frontend")]
datas += [("application", "./application")]
datas += copy_metadata('streamlit')


a = Analysis(
    ['streamlitWrapper.py'],
    pathex=['lessdrf-desktop/lib/python3.12/site-packages'],
    binaries=[],
    datas=datas,
    hiddenimports=["pronto", "st_aggrid", "streamlit_tree_select"],
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
    name='streamlitWrapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
