# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import PurePosixPath, Path

pkg_path = os.path.abspath(os.path.join('..', 'skytemple_randomizer'))
site_packages = next(p for p in sys.path if 'site-packages' in p)

additional_files = []
additional_datas = [
    (os.path.join(pkg_path, 'data'), 'data'),
    (os.path.join(pkg_path, '*.glade'), '.'),
    (os.path.join(site_packages, 'skytemple_files', '_resources'), 'skytemple_files/_resources'),
    (os.path.join('.', 'armips.exe'), 'skytemple_files/_resources'),
]

block_cipher = None


a = Analysis(['../skytemple_randomizer/main.py'],
             pathex=[os.path.abspath(os.path.join('..', 'skytemple_randomizer'))],
             datas=additional_datas,
             hiddenimports=['pkg_resources.py2_warn', 'packaging.version', 'packaging.specifiers',
                            'packaging.requirements', 'packaging.markers', '_sysconfigdata__win32_', 'win32api'],
             hookspath=[os.path.abspath(os.path.join('.', 'hooks'))],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='skytemple_randomizer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon=os.path.abspath(os.path.join('.', 'skytemple.ico')))

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               additional_files,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='skytemple_randomizer')
