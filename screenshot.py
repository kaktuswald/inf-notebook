import ctypes
from ctypes import windll,wintypes,create_string_buffer
from datetime import datetime
from PIL import Image,ImageGrab
from logging import getLogger
from os.path import exists,basename
import numpy as np

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from recog import recog

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
    def __init__(self, original, monochrome, filename):
        self.original = original
        self.monochrome = monochrome
        self.filename = filename

class Screenshot:
    width = 1280
    height = 720
    xy = None

    def __init__(self):
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

        self.buffer = create_string_buffer(self.height*self.width*3)

    def __del__(self):
        windll.gdi32.DeleteObject(self.bitmap)
        windll.gdi32.DeleteDC(self.screen_copy)
        windll.gdi32.DeleteDC(self.screen)

        logger.debug('Called Screenshot destuctor.')

    def __init__(self, area):
        self.area = area
    
    def shot(self):
        if self.xy is not None:
            windll.gdi32.BitBlt(self.screen_copy, 0, 0, self.width, self.height, self.screen, self.xy[0], self.xy[1], SRCCOPY)
            windll.gdi32.GetDIBits(self.screen_copy, self.bitmap, 0, self.height, ctypes.pointer(self.buffer), ctypes.pointer(self.bmi), DIB_RGB_COLORS)

            np_value = np.array(bytearray(self.buffer)).reshape(self.height, self.width, 3)[::-1,:,::-1]

            self.image = Image.fromarray(np_value)
        else:
            self.image = ImageGrab.grab(all_screens=True)

    def get(self):
        return self.image.convert('RGBA')

    def get_resultscreen(self):
        if not recog.get_is_screen_result(self.image):
            return None

        original = self.image.convert('RGBA')
        monochrome = original.convert('L')

        if not recog.get_is_result(monochrome):
            return None

        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(original, monochrome, filename)

def open_screenimage(filepath):
    if not exists(filepath):
        return None
    
    image = Image.open(filepath)
    filename = basename(filepath)

    return Screen(image, image.convert('L'), filename)