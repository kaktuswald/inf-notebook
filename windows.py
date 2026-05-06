from ctypes import (
    windll,
    c_bool, c_int, c_ulong, c_double,
    Structure,
    HRESULT,
    sizeof, byref,
    pointer, POINTER,
    WINFUNCTYPE,
    create_unicode_buffer,
)
from ctypes.wintypes import (
    BOOL, HANDLE, INT, UINT, DWORD,
    LPDWORD, LPWSTR, LPCWSTR,
    HWND, HMONITOR, HDC, LPRECT,
    POINT, RECT, LPARAM, 
    MAX_PATH,
)
from os import system,environ
from os.path import basename,exists
from pathlib import WindowsPath
from dataclasses import dataclass
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from infnotebook import productname

EVENT_OBJECT_LOCATIONCHANGE = 0x800B

class PROCESS_DPI_AWARENESS:
    PROCESS_DPI_UNAWARE             = 0
    PROCESS_SYSTEM_DPI_AWARE        = 1
    PROCESS_PER_MONITOR_DPI_AWARE   = 2

class SHOWWINDOW_COMMANDS:
    SW_HIDE             = 0
    SW_SHOWNORMAL       = 1
    SW_NORMAL           = 1
    SW_SHOWMINIMIZED    = 2
    SW_SHOWMAXIMIZED    = 3
    SW_MAXIMIZE         = 3
    SW_SHOWNOACTIVATE   = 4
    SW_SHOW             = 5
    SW_MINIMIZE         = 6
    SW_SHOWMINNOACTIVE  = 7
    SW_SHOWNA           = 8
    SW_RESTORE          = 9
    SW_SHOWDEFAULT      = 10
    SW_FORCEMINIMIZE    = 11

class WINEVENT:
    WINEVENT_OUTOFCONTEXT   = 0
    WINEVENT_SKIPOWNTHREAD  = 1
    WINEVENT_SKIPOWNPROCESS = 2
    WINEVENT_INCONTEXT      = 4

class HWND_CONSTANTS(HWND):
    HWND_NOTOPMOST  = -2
    HWND_TOPMOST    = -1
    HWND_TOP        = 0
    HWND_BOTTOM     = 1

class SWP_FLAGS:
    SWP_NOSIZE          = 0x0001
    SWP_NOMOVE          = 0x0002
    SWP_NOZORDER        = 0x0004
    SWP_NOREDRAW        = 0x0008
    SWP_NOACTIVE        = 0x0010
    SWP_DRAWFRAME       = 0x0020
    SWP_FRAMECHANGED    = 0x0020
    SWP_SHOWWINDOW      = 0x0040
    SWP_HIDEWINDOW      = 0x0080
    SWP_NOCOPYBITS      = 0x0100
    SWP_NOOWNERZORDER   = 0x0200
    SWP_NOREPOSITION    = 0x0200
    SWP_NOSENDCHANGING  = 0x0400
    SWP_DEFERERASE      = 0x2000
    SWP_ASYNCWINDOWPOS  = 0x4000

class MB_TYPES:
    MB_OK                   = 0x00000000
    MB_OKCANCEL             = 0x00000001
    MB_ABORTRETRYIGNORE     = 0x00000002
    MB_ESNOCANCEL           = 0x00000003
    MB_YESNO                = 0x00000004
    MB_RETRYCANCEL          = 0x00000005
    MB_CANCELTRYCONTINUE    = 0x00000006
    MB_HELP                 = 0x00004000

    MB_ICONSTOP             = 0x00000010
    MB_ICONERROR            = 0x00000010
    MB_ICONHAND             = 0x00000010
    MB_ICONQUESTION         = 0x00000020
    MB_ICONEXCLAMATION      = 0x00000030
    MB_ICONWARNING          = 0x00000030
    MB_ICONINFORMATION      = 0x00000040
    MB_ICONASTERISK         = 0x00000040

    MB_DEFBUTTON1           = 0x00000000
    MB_DEFBUTTON2           = 0x00000100
    MB_DEFBUTTON3           = 0x00000200
    MB_DEFBUTTON4           = 0x00000300

    MB_APPLMODAL            = 0x00000000
    MB_SYSTEMMODAL          = 0x00001000
    MB_TASKMODAL            = 0x00002000

    MB_DEFAULT_DESKTOP_ONLY = 0x00020000
    MB_RIGHT                = 0x00080000
    MB_RTLREADING           = 0x00100000
    MB_SETFOREGROUND        = 0x00010000
    MB_TOPMOST              = 0x00040000
    MB_SERVICE_NOTIFICATION = 0x00200000

class MONITORINFOF:
    MONITORINFOF_PRIMARY = 1

class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ('length', UINT),
        ('flags', UINT),
        ('showCmd', UINT),
        ('ptMinPosition', POINT),
        ('ptMaxPosition', POINT),
        ('rcNormalPosition', RECT),
        ('rcDevice', RECT),
    ]

class MONITORINFO(Structure):
    _fields_ = [
        ('cbSize', c_ulong),
        ('rcMonitor', RECT),
        ('rcWork', RECT),
        ('dwFlags', c_ulong),
    ]

@dataclass
class Rect:
    left: int = None
    top: int = None
    right: int = None
    bottom: int = None

    @property
    def width(self):
        return self.right - self.left
    
    @property
    def height(self):
        return self.bottom - self.top

@dataclass
class WindowPlacement():
    showstate: SHOWWINDOW_COMMANDS = None
    rect: Rect = None

@dataclass
class Monitor:
    rect: Rect = None
    is_primary: bool = None

enumWindowsProc = WINFUNCTYPE(
    c_bool,
    c_int,
    POINTER(c_int),
)

MonitorEnumProc = WINFUNCTYPE(
    c_int,
    HMONITOR,
    HDC,
    POINTER(RECT),
    c_double,
)

SetProcessDpiAwareness = windll.shcore.SetProcessDpiAwareness
SetProcessDpiAwareness.argtypes = (c_int,)
SetProcessDpiAwareness.restype = HRESULT

GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
GetWindowThreadProcessId.argtypes = (HWND, LPDWORD,)
GetWindowThreadProcessId.restype = DWORD

OpenProcess = windll.kernel32.OpenProcess
OpenProcess.argtypes = (DWORD, BOOL, DWORD,)
OpenProcess.restype = HANDLE

CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE,)
CloseHandle.restype = BOOL

QueryFullProcessImageNameW = windll.kernel32.QueryFullProcessImageNameW
QueryFullProcessImageNameW.argtypes = (HANDLE, DWORD, LPWSTR, LPDWORD,)
QueryFullProcessImageNameW.restype = BOOL

IsHungAppWindow = windll.user32.IsHungAppWindow
IsHungAppWindow.argtypes = (HWND,)
IsHungAppWindow.restype = BOOL

GetWindowTextLengthW = windll.user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = (HWND,)
GetWindowTextLengthW.restype = int

GetWindowTextW = windll.user32.GetWindowTextW
GetWindowTextW.argtypes = (HWND, LPWSTR, c_int,)
GetWindowTextW.restype = INT

EnumWindows = windll.user32.EnumWindows
EnumWindows.argtypes = (enumWindowsProc, LPARAM,)
EnumWindows.restype = BOOL

GetWindowRect = windll.user32.GetWindowRect
GetWindowRect.argtypes = (HWND, LPRECT,)
GetWindowRect.restype = BOOL

MessageBoxW = windll.user32.MessageBoxW
MessageBoxW.argtypes = (HWND, LPCWSTR, LPCWSTR, UINT,)
MessageBoxW.restype = INT

ShowWindow = windll.user32.ShowWindow
ShowWindow.argtypes = (HWND, c_int,)
ShowWindow.restype = BOOL

FindWindowW = windll.user32.FindWindowW
FindWindowW.argtypes = (LPCWSTR, LPCWSTR,)
FindWindowW.restype = HWND

EnumDisplayMonitors = windll.user32.EnumDisplayMonitors
EnumDisplayMonitors.argtypes = (HDC, POINTER(RECT), MonitorEnumProc, LPARAM,)
EnumDisplayMonitors.restype = BOOL

GetMonitorInfoW = windll.user32.GetMonitorInfoW
GetMonitorInfoW.argtypes = (HMONITOR, POINTER(MONITORINFO),)
GetMonitorInfoW.restype = BOOL

SetWindowPos =windll.user32.SetWindowPos
SetWindowPos.argtypes = (HWND, HWND, c_int, c_int, c_int, c_int, UINT,)
SetWindowPos.restype = BOOL

GetWindowPlacement = windll.user32.GetWindowPlacement
GetWindowPlacement.argtypes = (HWND, POINTER(WINDOWPLACEMENT),)
GetWindowPlacement.restype = BOOL

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

SetProcessDpiAwareness(PROCESS_DPI_AWARENESS.PROCESS_DPI_UNAWARE)

def get_filename(hwnd:int) -> str:
    processid = c_ulong()
    threadid = GetWindowThreadProcessId(hwnd, pointer(processid))
    if not threadid or not processid:
        return None

    hprocess = OpenProcess(0x0410, 0, processid.value)
    if not hprocess:
        return None

    filepath = create_unicode_buffer(MAX_PATH)
    length = DWORD(MAX_PATH)
    QueryFullProcessImageNameW(hprocess, 0, filepath, pointer(length))

    CloseHandle(hprocess)

    try:
        filename = basename(filepath.value)
        return filename
    except:
        return None

def find_window(title:str, filename:str) -> int:
    def foreach_window(hwnd:HWND, lParam:LPARAM) -> bool:
        if IsHungAppWindow(hwnd):
            return True
        
        length = GetWindowTextLengthW(hwnd)
        if not length:
            return True
        
        targettitle = create_unicode_buffer(length + 1)
        length = GetWindowTextW(hwnd, targettitle, length + 1)
        if targettitle.value != title:
            return True
        
        targetfilename = get_filename(hwnd)
        if targetfilename in [filename, None]:
            handles.append(hwnd)
        
        return True
    
    handles = []
    EnumWindows(enumWindowsProc(foreach_window), 0)

    return handles[0] if len(handles) == 1 else 0

def get_rect(hwnd:int) -> Rect:
    if hwnd == 0:
        return None
    
    rect = RECT()
    GetWindowRect(hwnd, pointer(rect))

    return Rect(
        left = rect.left,
        top = rect.top,
        right = rect.right,
        bottom = rect.bottom,
    )

def check_rectsize(rect:Rect) -> bool:
    return (rect.width, rect.height,) in rectsizes

def openfolder(dirpath:str) -> Exception|None:
    try:
        system(f'explorer.exe {dirpath}')
    except Exception as ex:
        return ex
    
    return None

def get_appdata_path() -> WindowsPath|None:
    path_str = environ.get('AppData')
    if not exists(path_str):
        return None
    
    path = WindowsPath(path_str)
    productpath = path.joinpath(productname)
    if not productpath.exists():
        productpath.mkdir()

    return productpath

def get_local_appdata_path() -> WindowsPath|None:
    '''ユーザのアプリケーションデータ格納先のパスを取得する

    一般にUsers\\ユーザ名\\AppData\\Local\\
    '''
    path_str = environ.get('LocalAppData')
    if not exists(path_str):
        return None
    
    path = WindowsPath(path_str)
    productpath = path.joinpath(productname)
    if not productpath.exists():
        productpath.mkdir()

    return productpath

def gethandle(title:str) -> int:
    hwnd = FindWindowW(None, title)
    if hwnd == 0:
        return None
    return hwnd

def show_messagebox(message:str, title:str) -> int:
    ret = MessageBoxW(0, message, title, MB_TYPES.MB_OK | MB_TYPES.MB_ICONSTOP)
    return ret

def maximize(hwnd:int) -> bool:
    ret = ShowWindow(hwnd, SHOWWINDOW_COMMANDS.SW_MAXIMIZE)
    return ret

def minimize(hwnd:int) -> bool:
    ret = ShowWindow(hwnd, SHOWWINDOW_COMMANDS.SW_MINIMIZE)
    return ret

def get_window_state(hwnd:int) -> WindowPlacement|None:
    placement = WINDOWPLACEMENT()
    placement.length = sizeof(WINDOWPLACEMENT)
    ret = GetWindowPlacement(hwnd, byref(placement))
    if not ret:
        return None

    rect = placement.rcNormalPosition
    return WindowPlacement(
        showstate = placement.showCmd,
        rect = Rect(
            left = rect.left,
            top = rect.top,
            right = rect.right,
            bottom = rect.bottom,
        ),
    )

def move_window(hwnd:int, left:int, top:int, width:int, height:int) -> bool:
    ret = SetWindowPos(
        hwnd,
        HWND_CONSTANTS.HWND_TOP,
        left,
        top,
        width,
        height,
        SWP_FLAGS.SWP_SHOWWINDOW,
    )
    return ret

def get_monitors() -> dict[int, Monitor]|None:
    def callback(hMonitor:HMONITOR, hdcMonitor:HDC, lprcMonitor:POINTER(RECT), dwData:LPARAM) -> BOOL:
        info = MONITORINFO()
        info.cbSize = sizeof(MONITORINFO)
        GetMonitorInfoW(hMonitor, byref(info))

        monitors[hMonitor] = Monitor(
            rect = Rect(
                left = info.rcMonitor.left,
                top = info.rcMonitor.top,
                right = info.rcMonitor.right,
                bottom = info.rcMonitor.bottom,
            ),
            is_primary = info.dwFlags & MONITORINFOF.MONITORINFOF_PRIMARY,
        )
        
        return True
    
    monitors = {}
    if not EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0):
        return None
    
    return monitors

if __name__ == '__main__':
    gamewindowtitle = 'beatmania IIDX INFINITAS'
    exename = 'bm2dx.exe'

    print(find_window(gamewindowtitle, exename))
