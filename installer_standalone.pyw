import sys
from sys import argv
from os import remove
from os.path import exists
from tkinter import Tk,BooleanVar,StringVar,TOP,BOTTOM,LEFT,E,NORMAL,DISABLED
from tkinter.ttk import Frame,Entry,Label,Button,Checkbutton
from tkinter import filedialog
from shutil import rmtree
from threading import Thread,Event
from pathlib import WindowsPath
from zipfile import ZipFile
from subprocess import Popen

from infnotebook import productname,exe_filename
from appdata import LocalConfig

version_filename: str = 'version.txt'
'''バージョンファイル

インストール済みのバージョンを確認するためのファイル
0.18.0.0以降のリザルト手帳のインストールされているフォルダの中にある
'''

class InstallerWindow:
    installtarget_dirpath: WindowsPath = None
    product_dirpath: WindowsPath = None
    targetversion: str = None
    zipfilepath: WindowsPath = None
    is_installing = False

    def __init__(self, config: LocalConfig, debug=False):
        self.config = config
        self.debug = debug

        if config.installed_dirpath is not None:
            self.installtarget_dirpath = config.installed_dirpath
        else:
            self.installtarget_dirpath = WindowsPath(argv[0])
        
        if hasattr(sys, '_MEIPASS'):
            resourcedirpath = WindowsPath(sys._MEIPASS)
        else:
            resourcedirpath = WindowsPath(WindowsPath.cwd())
        
        self.root = Tk()
        self.root.resizable(0, 0)
        self.root.protocol('WM_DELETE_WINDOW', self.onclick_close)
    
        if debug:
            self.add_frame_is_debug_enabled()
        self.add_frame_displays()
        self.add_frame_message()
        self.add_frame_checkbutton()
        self.add_frame_buttons()

        if resourcedirpath.exists():
            self.root.iconbitmap(resourcedirpath.joinpath('icon.ico') )
            
            version_filepath = resourcedirpath.joinpath('version.txt')
            if version_filepath.exists():
                with open(version_filepath) as f:
                    self.targetversion = f.read()           
            
            self.zipfilepath = resourcedirpath.joinpath(f'inf-notebook.zip')

            self.root.title(f'リザルト手帳 {self.targetversion} インストーラ')
        else:
            self.root.title(f'リザルト手帳 インストーラ')

            self.var_message.set('インストールできるファイルが見つかりません。')

            self.button_install['state'] = DISABLED

    def onclick_close(self):
        if not self.is_installing:
            self.close()
    
    def add_frame_is_debug_enabled(self):
        frame = Frame(
            self.root,
            padding=10,
        )

        Label(
            frame,
            text='- デバッグモードが有効になります -',
        ).pack(side=LEFT)

        frame.pack(side=TOP)

    def add_frame_displays(self):
        self.var_installtarget_dirpath = StringVar(value=str(self.installtarget_dirpath))
        self.var_message = StringVar()

        self.check_is_installed()

        frame = Frame(
            self.root,
            padding=10,
        )

        Label(
            frame,
            text='インストール先フォルダ',
            padding=5,
        ).pack(side=LEFT)

        Entry(
            frame,
            textvariable=self.var_installtarget_dirpath,
            width=60,
            state='readonly',
        ).pack(side=LEFT)
        
        self.button_select = Button(
            frame,
            text='...',
            command=self.open_target_directory_select_dialog,
        )
        self.button_select.pack()

        frame.pack(side=TOP)

    def add_frame_message(self):
        frame = Frame(
            self.root,
            padding=20,
        )

        Label(
            frame,
            textvariable=self.var_message,
            width=80,
        ).pack(side=LEFT)

        frame.pack(side=TOP)

    def add_frame_checkbutton(self):
        frame = Frame(
            self.root,
            padding=20,
        )

        self.var_autoclose = BooleanVar(value=True)
        self.var_starttool = BooleanVar(value=True)

        Checkbutton(
            frame,
            text='インストールの完了でインストーラを終了する',
            variable=self.var_autoclose,
        ).pack(side=LEFT)

        Checkbutton(
            frame,
            text='終了時にリザルト手帳を起動する',
            variable=self.var_starttool,
        ).pack(side=LEFT)

        frame.pack(side=TOP)
    
    def add_frame_buttons(self):
        frame = Frame(
            self.root,
            padding=10,
        )

        self.button_install = Button(
            frame,
            text='インストール',
            command=self.launch_install,
            padding=10,
        )
        self.button_install.pack(side=LEFT)

        self.button_close = Button(
            frame,
            text='閉じる',
            command=self.close,
            padding=10,
        )
        self.button_close.pack(side=LEFT)

        frame.pack(side=BOTTOM, anchor=E)

    def loop(self):
        self.root.mainloop()
    
    def open_target_directory_select_dialog(self):
        directorypath = filedialog.askdirectory(
            initialdir=self.var_installtarget_dirpath.get()
        )
        if exists(directorypath):
            self.var_installtarget_dirpath.set(directorypath)
            self.check_is_installed()
    
    def close(self):
        if self.var_starttool.get():
            exe_filepath = self.product_dirpath.joinpath(exe_filename)
            if exe_filepath.exists():
                Popen([exe_filepath], cwd=exe_filepath.parent)
        
        self.root.destroy()
    
    def check_is_installed(self):
        targetpath = WindowsPath(self.var_installtarget_dirpath.get()).absolute()

        target_dirname = targetpath.name
        exe_filepath = targetpath.joinpath(exe_filename)
        if target_dirname == productname and exe_filepath.exists():
            self.installtarget_dirpath = targetpath.parent
        else:
            self.installtarget_dirpath = targetpath

        self.product_dirpath = self.installtarget_dirpath.joinpath(productname)

        self.display_installed_state()

    def display_installed_state(self):
        if not self.product_dirpath.exists():
            self.var_message.set('ここにリザルト手帳はインストールされていません。')
            return

        exe_filepath = self.product_dirpath.joinpath(exe_filename)
        if not exe_filepath.exists():
            self.var_message.set('ここにリザルト手帳はインストールされていません。')
            return

        version = self.get_version()
        if version is not None:
            self.var_message.set(f'バージョン {version} がインストールされています。')
        else:
            self.var_message.set('リザルト手帳がインストールされています。')
        
    def get_version(self):
        version_filepath = self.product_dirpath.joinpath(version_filename)
        if version_filepath.exists():
            with version_filepath.open('r') as f:
                version = f.read()
            return version
        
        return None
    
    def launch_install(self):
        self.button_select['state'] = DISABLED
        self.button_install['state'] = DISABLED
        self.button_close['state'] = DISABLED

        self.is_installing = True

        self.event_complete = Event()
        self.event_failure = Event()
        Thread(target=self.install).start()

        self.wait_complete()
    
    def install(self):
        lib_dirpath = self.product_dirpath.joinpath('lib')
        if lib_dirpath.exists():
            self.var_message.set('不要なファイルを削除しています...')
            try:
                rmtree(lib_dirpath)
            except Exception as ex:
                self.var_message.set('不要なファイルの削除に失敗しました。')
                self.event_failure.set()
                return

        if self.zipfilepath and self.zipfilepath.exists():
            self.var_message.set('圧縮ファイルを解凍・コピーしています...')
            with ZipFile(self.zipfilepath) as z:
                z.extractall(self.installtarget_dirpath)

            self.var_message.set(f'バージョン {self.targetversion} のインストールが完了しました。')
        else:
            self.var_message.set(f'インストールするファイルが見つかりませんでした。')
            self.event_failure.set()
            return

        self.var_message.set('圧縮ファイルを解凍・コピーしています...')
        with ZipFile(self.zipfilepath) as z:
            z.extractall(self.installtarget_dirpath)
        
        self.var_message.set(f'バージョン {self.targetversion} のインストールが完了しました。')

        self.event_complete.set()
        
    def wait_complete(self):
        if not self.event_complete.is_set() and not self.event_failure.is_set():
            self.root.after(100, self.wait_complete)
            return
        
        self.is_installing = False

        self.button_close['state'] = NORMAL

        if self.event_complete.is_set():
            debug_filepath = self.product_dirpath.joinpath('DEBUG')
            if self.debug:
                if not exists(debug_filepath):
                    open(debug_filepath, 'w').close()
            else:
                if exists(debug_filepath):
                    remove(debug_filepath)

            self.config.installed_dirpath = self.installtarget_dirpath
            self.config.save()
            
            if self.var_autoclose.get():
                self.close()

def open_installer_window(debug=False):
    config = LocalConfig()

    window = InstallerWindow(config, debug)
    window.loop()

if __name__ == '__main__':
    open_installer_window()
