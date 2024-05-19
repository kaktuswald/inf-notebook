import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# 'packages': ['os'] is used as example only
build_exe_options = {
    'include_files': [
        'icon.ico',
        'readme.txt',
    ]
}

# base='Win32GUI' should be used only for Windows GUI app
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = (
    [
        Executable(
            'installer.py',
            copyright='Copyright (C) 2024',
            base=base,
            shortcut_name=u'リザルト手帳 インストーラ',
            shortcut_dir=u'リザルト手帳 インストーラ',
            icon='../icon.ico',
            target_name='infnotebook_installer'
        )
    ]
)

setup(
    name=u'INF NOTEBOOK installer',
    version='1.0.0.0',
    description=u'INF NOTEBOOK installer',
    options={'build_exe': build_exe_options},
    executables=executables
)
