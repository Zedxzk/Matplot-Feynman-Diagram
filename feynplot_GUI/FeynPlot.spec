# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['feynplot_gui/__main__.py'],
    pathex=['/home/zed/pyfeynmandiagram/', '/home/zed/pyfeynmandiagram/feynplot_GUI'],
    binaries=[
        # ***** 添加或修改以下行，以包含 libjpeg 和 libtiff 库 *****
        ('/home/zed/miniconda3/envs/dpl/lib/libjpeg.so.8.3.2', '.'), # 最具体的 libjpeg.so.8 版本
        ('/home/zed/miniconda3/envs/dpl/lib/libtiff.so.6.0.2', '.')  # 最具体的 libtiff.so.6 版本
        # **********************************************************
    ],
    datas=[],
    hiddenimports=['feynplot'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # ***** 保持 excludes 列表不变，以避免系统库冲突 *****
    excludes=[
        'libtiff.so.6',   # 排除这个符号链接，强制使用我们手动包含的具体版本
        'libjpeg.so',     # 排除这些符号链接，强制使用我们手动包含的具体版本
        'libjpeg.so.8'
    ],
    # ***************************************************
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
    name='FeynPlot',
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