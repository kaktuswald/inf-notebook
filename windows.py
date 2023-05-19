from ctypes import windll,c_bool,c_int,pointer,POINTER,WINFUNCTYPE,create_unicode_buffer
from ctypes.wintypes import RECT

def search(title):
    enumWindowsProc = WINFUNCTYPE(c_bool, c_int, POINTER(c_int))

    handles = []
    def foreach_window(hWnd, lParam):
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buff = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buff, length + 1)
        if buff.value == title:
            handles.append(hWnd)
    windll.user32.EnumWindows(enumWindowsProc(foreach_window), 0)

    return handles[0] if len(handles) else 0

def get_handle(title):
    wresult = windll.user32.FindWindowW(None, title)
    if wresult != 0:
        return wresult
    
    exwresult = windll.user32.FindWindowExW(None, None, None, title)
    if exwresult != 0:
        return exwresult
    
    return 0

def get_rect(handle):
    if handle == 0:
        return None
    
    rect = RECT()
    windll.user32.GetWindowRect(handle, pointer(rect))
    return rect

if __name__ == '__main__':
    h = get_handle('beatmania IIDX INFINITAS')
    rect = get_rect(h)
    print(h, rect)
