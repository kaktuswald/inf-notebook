import ctypes
from ctypes import windll,wintypes,create_string_buffer
from datetime import datetime
from PIL import Image
from logging import getLogger
from os.path import exists,basename
import numpy as np

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
PW_CLIENTONLY = 1

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]

class RGBQUAD(ctypes.Structure):
    _fields_ = [
        ('rgbRed', ctypes.c_byte),
        ('rgbGreen', ctypes.c_byte),
        ('rgbBlue', ctypes.c_byte),
        ('rgbReserved', ctypes.c_byte),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', ctypes.POINTER(RGBQUAD))
    ]

class Screen:
    def __init__(self, np_value, filename):
        self.np_value = np_value

        image = Image.fromarray(np_value[::-1, :, ::-1])
        self.original = image.convert('RGB')
        self.monochrome = image.convert('L')
        self.filename = filename

class Capture:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.bmi = BITMAPINFO()
        self.bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.bmi.bmiHeader.biWidth = self.width
        self.bmi.bmiHeader.biHeight = self.height
        self.bmi.bmiHeader.biPlanes = 1
        self.bmi.bmiHeader.biBitCount = 24
        self.bmi.bmiHeader.biCompression = 0
        self.bmi.bmiHeader.biSizeImage = 0

        self.screen = windll.gdi32.CreateDCW("DISPLAY", None, None, None)
        self.screen_copy = windll.gdi32.CreateCompatibleDC(self.screen)
        self.bitmap = windll.gdi32.CreateCompatibleBitmap(self.screen, self.width, self.height)

        windll.gdi32.SelectObject(self.screen_copy, self.bitmap)

        self.buffer = create_string_buffer(self.height * self.width * 3)
    
    def shot(self, left, top):
        windll.gdi32.BitBlt(self.screen_copy, 0, 0, self.width, self.height, self.screen, left, top, SRCCOPY)
        windll.gdi32.GetDIBits(self.screen_copy, self.bitmap, 0, self.height, ctypes.pointer(self.buffer), ctypes.pointer(self.bmi), DIB_RGB_COLORS)

        return np.array(bytearray(self.buffer)).reshape(self.height, self.width, 3)

    def __del__(self):
        windll.gdi32.DeleteObject(self.bitmap)
        windll.gdi32.DeleteDC(self.screen_copy)
        windll.gdi32.DeleteDC(self.screen)

        logger.debug('Called Screenshot destuctor.')

class Screenshot:
    xy = None

    def __init__(self, checkloading_value):
        self.checkloading = Capture(define.is_loading_area['width'], define.is_loading_area['height'])
        self.capture = Capture(define.width, define.height)

        self.checkloading_value = checkloading_value

    def __del__(self):
        del self.checkloading
        del self.capture

    def is_loading(self):
        if self.xy is None:
            return None
        
        x = self.xy[0] + define.is_loading_area['left']
        y = self.xy[1] + define.is_loading_area['top']
        return np.array_equal(self.checkloading.shot(x, y), self.checkloading_value)

    def shot(self):
        if self.xy is None:
            return None
        
        self.np_value = self.capture.shot(self.xy[0], self.xy[1])

    def get_image(self):
        convert = self.np_value[::-1, :, ::-1]
        return Image.fromarray(convert).convert('RGB')

    def get_resultscreen(self):
        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(self.np_value, filename)

def open_screenimage(filepath):
    if not exists(filepath):
        return None
    
    image = Image.open(filepath).convert('RGB')
    filename = basename(filepath)

    return Screen(np.array(image)[::-1, :, ::-1], filename)
