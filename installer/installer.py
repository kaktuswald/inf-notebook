from os.path import abspath,dirname,join,exists
from tkinter import Tk,StringVar,TOP,BOTTOM,LEFT,E,NORMAL,DISABLED
from tkinter.ttk import Frame,Entry,Label,Button
from tkinter import filedialog
from shutil import unpack_archive,rmtree,copytree
from threading import Thread

temporary_dirname = 'temp'
icon_filename = 'icon.ico'
exe_filename = 'infnotebook.exe'
version_filename = 'version.txt'
zip_filename = 'inf-notebook.zip'

class Installer:
    def __init__(self):
        self.root = Tk()
        self.root.title('リザルト手帳 インストーラ')
        self.root.iconbitmap(icon_filename)
        self.root.resizable(0, 0)
    
        self.add_frame_displays()
        self.add_frame_message()
        self.add_frame_buttons()

    def add_frame_displays(self):
        self.var_target_directory_path = StringVar(value=abspath(dirname(__file__)))
        self.var_message = StringVar()

        self.display_installed_state()

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
            textvariable=self.var_target_directory_path,
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
            initialdir=self.var_target_directory_path.get()
        )
        if len(directorypath) > 0:
            self.var_target_directory_path.set(directorypath)
            self.display_installed_state()
    
    def close(self):
        self.root.destroy()
    
    def display_installed_state(self):
        version = self.get_version()
        if version is not None:
            self.var_message.set(f'バージョン {version} がインストールされています。')
            return
        
        exe_filepath = join(self.var_target_directory_path.get(), exe_filename)
        if exists(exe_filepath):
            self.var_message.set('リザルト手帳がインストールされています。')
            return

        self.var_message.set('ここにリザルト手帳はインストールされていません。')
        
    def get_version(self):
        version_filepath = join(self.var_target_directory_path.get(), version_filename)
        if exists(version_filepath):
            with open(version_filepath, 'r') as f:
                version = f.read()
            return version
        
        return None
    
    def launch_install(self):
        self.button_select['state'] = DISABLED
        self.button_install['state'] = DISABLED
        self.button_close['state'] = DISABLED
        Thread(target=self.install, ).start()
    
    def install(self):
        target_dirpath = self.var_target_directory_path.get()

        lib_dirpath = join(target_dirpath, 'lib')
        if exists(lib_dirpath):
            self.var_message.set('不要なファイルを削除しています...')
            rmtree(lib_dirpath)

        work_dirpath = dirname(__file__)

        zip_filepath = join(work_dirpath, zip_filename)
        self.var_message.set('圧縮ファイルを解凍しています...')
        unpack_archive(zip_filepath, temporary_dirname)

        temporary_dirpath = join(work_dirpath, temporary_dirname)
        self.var_message.set('圧縮ファイルをコピーしています...')
        copytree(temporary_dirpath, target_dirpath, dirs_exist_ok=True)

        self.var_message.set('一時ファイルを削除しています...')
        rmtree(temporary_dirpath)

        self.var_message.set(f'バージョン {self.get_version()} のインストールが完了しました。')

        self.button_close['state'] = NORMAL

if __name__ == '__main__':
    installer = Installer()
    installer.loop()
