# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# python-hslog 경로 추가
hslog_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'python-hslog')
sys.path.append(hslog_path)

a = Analysis(
    ['gui.py'],
    pathex=[hslog_path],  # python-hslog 경로 추가
    binaries=[],
    datas=[
        ('settings.ini', '.'),
        ('.env', '.') if os.path.exists('.env') else ('.env.example', '.'),
        ('python-hslog', 'python-hslog')  # python-hslog 폴더 전체 포함
    ],
    hiddenimports=['hslog', 'hslog.parser', 'hslog.export', 'hearthstone', 'hearthstone.enums', 'hearthstone.entities'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='hs-chzzk-streamer-client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='hs-chzzk-streamer-client',
)
