import sys
from cx_Freeze import setup, Executable

from version import version
from infnotebook import icon_filename

# Dependencies are automatically detected, but it might need fine tuning.
# 'packages': ['os'] is used as example only
build_exe_options = {
    'excludes': [
        'distutils',
        'lib2to3',
        'setuptools',
        'unittest',
        'test',
        'zipp',
        'fontTools'
    ],
    'include_msvcr': True,
    'include_files': [
        'resources/',
        'export/',
        'readme.txt',
        'version.txt',
        icon_filename
    ]
}

# base='Win32GUI' should be used only for Windows GUI app
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = (
    [
        Executable(
            'main.pyw',
            copyright='Copyright (C) 2022-2024',
            base=base,
            shortcut_name=u'ビートマニアリザルト手帳',
            shortcut_dir=u'ビートマニアリザルト手帳',
            icon=icon_filename,
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
