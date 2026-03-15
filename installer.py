from sys import argv
from os.path import exists
from tkinter import Tk,BooleanVar,StringVar,TOP,BOTTOM,LEFT,E,NORMAL,DISABLED
from tkinter.ttk import Frame,Entry,Label,Button,Combobox,Checkbutton
from tkinter import filedialog
from shutil import rmtree
from threading import Thread
from requests import get
from pathlib import WindowsPath
from zipfile import ZipFile
from io import BytesIO
from subprocess import Popen

from infnotebook import productname,exe_filename,icon_filename
from appdata import LocalConfig

version_installer: str = '2.0.0.0'

version_filename: str = 'version.txt'
'''バージョンファイル

インストール済みのバージョンを確認するためのファイル
0.18.0.0以降のリザルト手帳のインストールされているフォルダの中にある
'''

url_releases: str = 'https://api.github.com/repos/kaktuswald/inf-notebook/releases'

get_connectiontimeout = 5
get_downloadtimeout = 60

class InstallerWindow:
    def __init__(self, config: LocalConfig):
        self.config = config
        self.releases = {}

        if config.installed_dirpath is not None:
            self.target_dirpath = config.installed_dirpath
        else:
            self.target_dirpath = WindowsPath(argv[0])
        
        self.root = Tk()
        self.root.title(f'リザルト手帳 インストーラ {version_installer}')
        self.root.iconbitmap(icon_filename)
        self.root.resizable(0, 0)
    
        self.add_frame_displays()
        self.add_frame_releases()
        self.add_frame_message()
        self.add_frame_checkbutton()
        self.add_frame_buttons()

    def add_frame_displays(self):
        self.var_target_dirpath = StringVar(value=str(self.target_dirpath))
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
            textvariable=self.var_target_dirpath,
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

    def add_frame_releases(self):
        self.get_releases()

        self.var_selected_release = StringVar()
        if len(self.releases) > 0:
            self.var_selected_release.set([*self.releases.keys()][0])

        self.frame_releases = Frame(
            self.root,
            padding=10,
        )

        Label(
            self.frame_releases,
            text='バージョン選択',
            padding=5,
        ).pack(side=LEFT)

        self.combobox_version = Combobox(
            self.frame_releases,
            values=[*self.releases.keys()],
            textvariable=self.var_selected_release,
            width=60,
            state='readonly',
        )
        self.combobox_version.pack(side=LEFT)
        
        self.frame_releases.pack(side=TOP)

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

        self.var_starttool = BooleanVar(value=True)

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

        if len(self.releases) == 0:
            self.button_install['state'] = DISABLED

        frame.pack(side=BOTTOM, anchor=E)

    def get_releases(self):
        response = get(url_releases)
        if not response.ok:
            self.var_message.set(f'ダウンロード可能なリストの取得に失敗しました。')
            return

        jsons: list[dict] = response.json()
        for target in jsons:
            if not 'name' in target.keys():
                continue
            if not 'draft' in target.keys() or target['draft']:
                print('draft!!')
                continue
            if not 'prerelease' in target.keys() or target['prerelease']:
                continue
            if not 'assets' in target.keys() or type(target['assets']) is not list or len(target['assets']) == 0:
                continue
            if type(target['assets'][0]) is not dict or not 'browser_download_url' in target['assets'][0].keys():
                continue

            for asset in target['assets']:
                if target['tag_name'] in asset['name']:
                    self.releases[target['name']] = asset['browser_download_url']
                    break
        
    def loop(self):
        self.root.mainloop()
    
    def open_target_directory_select_dialog(self):
        directorypath = filedialog.askdirectory(
            initialdir=self.var_target_dirpath.get()
        )
        if exists(directorypath):
            self.var_target_dirpath.set(directorypath)
            self.check_is_installed()
    
    def close(self):
        if self.var_starttool.get():
            exe_filepath = self.product_dirpath.joinpath(exe_filename)
            if exe_filepath.exists():
                Popen(exe_filepath)
        
        self.root.destroy()
    
    def check_is_installed(self):
        targetpath = WindowsPath(self.var_target_dirpath.get()).absolute()

        target_dirname = targetpath.name
        exe_filepath = targetpath.joinpath(exe_filename)
        if target_dirname == productname and exe_filepath.exists():
            self.target_dirpath = targetpath.parent
        else:
            self.target_dirpath = targetpath

        self.product_dirpath = self.target_dirpath.joinpath(productname)

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
        self.combobox_version['state'] = DISABLED
        self.button_install['state'] = DISABLED
        self.button_close['state'] = DISABLED

        Thread(target=self.install).start()
    
    def install(self):
        downloadurl = self.releases[self.var_selected_release.get()]

        zipdata: bytes | None = None

        self.var_message.set('ダウンロードしています...')
        try:
            buffer = BytesIO()

            with get(downloadurl, stream=True, timeout=(get_connectiontimeout, get_downloadtimeout,)) as response:
                response.raise_for_status()

                total = int(response.headers.get('Content-Length', 0))
                downloaded = 0

                for chunk in response.iter_content(chunk_size=1024*1024):
                    if not chunk:
                        continue

                    buffer.write(chunk)
                    downloaded += len(chunk)

                    percent = int(downloaded / total * 100) if total > 0 else None
                    self.var_message.set(f'ダウンロードしています... {downloaded/1000000:,.1f} MB / {total/1000000:,.1f} MB ({percent} %)')
                
            if response.ok:
                buffer.seek(0)
                zipdata = buffer
            else:
                self.var_message.set(f'ダウンロードに失敗しました。({response.content})')

        except Exception as e:
            self.var_message.set(f'ダウンロードに失敗しました。({e})')
            return
        
        if zipdata is None:
            return
        
        lib_dirpath = self.product_dirpath.joinpath('lib')
        if lib_dirpath.exists():
            self.var_message.set('不要なファイルを削除しています...')
            try:
                rmtree(lib_dirpath)
            except Exception as ex:
                self.var_message.set('不要なファイルの削除に失敗しました。')
                self.button_close['state'] = NORMAL
                return

        self.var_message.set('圧縮ファイルを解凍・コピーしています...')
        with ZipFile(zipdata) as z:
            z.extractall(self.target_dirpath)

        self.var_message.set(f'バージョン {self.get_version()} のインストールが完了しました。')

        self.config.installed_dirpath = self.target_dirpath
        self.config.save()

        self.button_close['state'] = NORMAL

if __name__ == '__main__':
    config = LocalConfig()

    config.installer_filepath = WindowsPath(argv[0])
    config.save()

    window = InstallerWindow(config)
    window.loop()
