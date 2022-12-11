import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# 'packages': ['os'] is used as example only
build_exe_options = {
    'excludes': [
        'distutils',
        'lib2to3',
        'setuptools',
        'unittest',
        'test',
        'zipp'
    ],
    'include_msvcr': True,
    'include_files': [
        'resources/',
        'readme.txt',
        'icon.ico'
    ]
}

# base='Win32GUI' should be used only for Windows GUI app
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

if not os.path.exists('VERSION.txt'):
    sys.exit()
with open('VERSION.txt') as f:
    version = f.read()

executables = (
    [
        Executable(
            'main.pyw',
            copyright='Copyright (C) 2022',
            base=base,
            shortcut_name=u'ビートマニアリザルト手帳',
            shortcut_dir=u'ビートマニアリザルト手帳',
            icon='icon.ico',
            target_name='infnotebook'
        )
    ]
)

setup(
    name=u'INF NOTEBOOK',
    version=version,
    description=u'INF NOTEBOOK',
    options={'build_exe': build_exe_options},
    executables=executables
)
