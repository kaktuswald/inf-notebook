from ctypes import (
    windll,
    c_bool,
    c_int,
    c_ulong,
    pointer,
    POINTER,
    WINFUNCTYPE,
    create_unicode_buffer,
)
from ctypes.wintypes import RECT,DWORD,MAX_PATH
from os import system,environ
from os.path import basename,exists
from pathlib import WindowsPath

from infnotebook import productname

class PROCESS_DPI_AWARENESS:
    PROCESS_DPI_UNAWARE = 0
    PROCESS_SYSTEM_DPI_AWARE = 1
    PROCESS_PER_MONITOR_DPI_AWARE = 2

rectsizes = (
    (1920, 1080),
    (1536, 864),
    (1280, 720),
    (1097, 617)
)
'''INFINITASの画面サイズの候補

ディスプレイの拡大/縮小設定によって取得できるINFINITASの画面サイズが変化するため、
いずれかに一致していたらOKとする
'''

windll.shcore.SetProcessDpiAwareness(PROCESS_DPI_AWARENESS.PROCESS_DPI_UNAWARE)

def get_filename(wHnd):
    pId = c_ulong()
    windll.user32.GetWindowThreadProcessId(wHnd, pointer(pId))
    if not pId:
        return 0

    pHnd = windll.kernel32.OpenProcess(0x0410, 0, pId)
    if not pHnd:
        return 0

    filepath = create_unicode_buffer(MAX_PATH)
    length = DWORD(MAX_PATH)
    windll.kernel32.QueryFullProcessImageNameW(pHnd, 0, pointer(filepath), pointer(length))
    filename = basename(filepath.value)

    return filename

def find_window(title, filename):
    enumWindowsProc = WINFUNCTYPE(c_bool, c_int, POINTER(c_int))

    handles = []
    def foreach_window(hWnd, lParam):
        if windll.user32.IsHungAppWindow(hWnd):
            return True
        filename = get_filename(hWnd)
        length = windll.user32.GetWindowTextLengthW(hWnd)
        if not length:
            return True
        buff = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buff, length + 1)
        if buff.value != title:
            return True
        if get_filename(hWnd) in [filename, 0]:
            handles.append(hWnd)
        return True
    windll.user32.EnumWindows(enumWindowsProc(foreach_window), 0)

    return handles[0] if len(handles) == 1 else 0

def get_rect(handle):
    if handle == 0:
        return None
    
    rect = RECT()
    windll.user32.GetWindowRect(handle, pointer(rect))
    return rect

def check_rectsize(rect: RECT) -> bool:
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    return (width, height) in rectsizes

def openfolder(dirpath: str):
    try:
        system(f'explorer.exe {dirpath}')
    except Exception as ex:
        return ex
    
    return None

def get_appdata_path() -> WindowsPath:
    path_str = environ.get('AppData')
    if not exists(path_str):
        return None
    
    path = WindowsPath(path_str)
    productpath = path.joinpath(productname)
    if not productpath.exists():
        productpath.mkdir()

    return productpath

def get_local_appdata_path() -> WindowsPath:
    path_str = environ.get('LocalAppData')
    if not exists(path_str):
        return None
    
    path = WindowsPath(path_str)
    productpath = path.joinpath(productname)
    if not productpath.exists():
        productpath.mkdir()

    return productpath

def gethandle(title: str):
    handle = windll.user32.FindWindowW(None, title)
    if handle == 0:
        return None
    return handle

def show_messagebox(message: str, title: str):
    MB_OK = 0x0000
    windll.user32.MessageBoxW(0, message, title, MB_OK)

if __name__ == '__main__':
    gamewindowtitle = 'beatmania IIDX INFINITAS'
    exename = 'bm2dx.exe'

    print(find_window(gamewindowtitle, exename))
