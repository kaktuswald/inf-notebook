import ctypes
from ctypes import windll,c_bool,c_int,pointer,POINTER,WINFUNCTYPE,create_unicode_buffer
from ctypes.wintypes import RECT,DWORD,MAX_PATH
from os.path import basename

def get_filename(wHnd):
    pId = ctypes.c_ulong()
    windll.user32.GetWindowThreadProcessId(wHnd, ctypes.pointer(pId))
    if not pId:
        return 0

    pHnd = windll.kernel32.OpenProcess(0x0410, 0, pId)
    if not pHnd:
        return 0

    filepath = ctypes.create_unicode_buffer(MAX_PATH)
    length = DWORD(MAX_PATH)
    windll.kernel32.QueryFullProcessImageNameW(pHnd, 0, ctypes.pointer(filepath), ctypes.pointer(length))
    filename = basename(filepath.value)

    return filename

def find_window(title, filename):
    enumWindowsProc = WINFUNCTYPE(c_bool, c_int, POINTER(c_int))

    handles = []
    def foreach_window(hWnd, lParam):
        length = windll.user32.GetWindowTextLengthW(hWnd)
        if not length:
            return True
        buff = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buff, length + 1)
        if buff.value != title:
            return True
        if get_filename(hWnd) == filename:
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

if __name__ == '__main__':
    windowtitle = 'beatmania IIDX INFINITAS'
    exename = 'bm2dx.exe'

    print(find_window(windowtitle, exename))
