import sys
from cx_Freeze import setup, Executable

from installer import version_installer
from infnotebook import icon_filename

# Dependencies are automatically detected, but it might need fine tuning.
# 'packages': ['os'] is used as example only
build_exe_options = {
    'include_files': [
        icon_filename,
        'installer_readme.txt',
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
            icon=icon_filename,
            target_name='infnotebook_installer'
        )
    ]
)

setup(
    name=u'INF NOTEBOOK installer',
    version=version_installer,
    description=u'INF NOTEBOOK installer',
    options={'build_exe': build_exe_options},
    executables=executables
)
