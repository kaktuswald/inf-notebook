import ctypes
from ctypes import windll,wintypes,create_string_buffer
from datetime import datetime
from threading import Thread,Event
from queue import Queue,Full
from time import time
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

import numpy as np
from PIL import Image

from define import define
from resources import resource
from recog import Recognition as recog
from setting import Setting
from windows import find_window,get_rect,check_rectsize
from collection_uploader import CollectionUploader
from capture import (
    Screen,
    thread_time_wait_nonactive,
    thread_time_wait_loading,
    thread_time_normal,
    thread_time_result,
    thread_time_musicselect,
)

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

class Capture:
    def __init__(self, name, width, height):
        self.name = name
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

        self.screen = windll.gdi32.CreateDCW('DISPLAY', None, None, None)
        self.screen_copy = windll.gdi32.CreateCompatibleDC(self.screen)
        self.bitmap = windll.gdi32.CreateCompatibleBitmap(self.screen, self.width, self.height)

        windll.gdi32.SelectObject(self.screen_copy, self.bitmap)

        self.buffer = create_string_buffer(self.height * self.width * 3)
    
    def shot(self, left, top):
        windll.gdi32.BitBlt(self.screen_copy, 0, 0, self.width, self.height, self.screen, left, top, SRCCOPY)
        windll.gdi32.GetDIBits(self.screen_copy, self.bitmap, 0, self.height, ctypes.pointer(self.buffer), ctypes.pointer(self.bmi), DIB_RGB_COLORS)

        return np.array(bytearray(self.buffer), dtype=np.uint8).reshape(self.height, self.width, 3)

    def __del__(self):
        windll.gdi32.DeleteObject(self.bitmap)
        windll.gdi32.DeleteDC(self.screen_copy)
        windll.gdi32.DeleteDC(self.screen)

        logger.debug(f'Called Screenshot({self.name}) destructor.')

class Screenshot:
    xy: tuple[int]|None = None
    np_value: np.ndarray|None = None

    def __init__(self):
        self.checkscreens = []
        for screenname, item in resource.screenrecognition['get_screen'].items():
            lefttop = (item['area']['left'], item['area']['top'],)
            capture = Capture(screenname, item['area']['width'], item['area']['height'])
            self.checkscreens.append((screenname, lefttop, capture, item['value'],))
        
        self.capture = Capture('capture', define.width, define.height)

    def get_screen(self):
        if self.xy is None:
            return None
        
        results = []
        for screen, pos, capture, value in self.checkscreens:
            x = self.xy[0] + pos[0]
            y = self.xy[1] + pos[1]

            if np.sum(capture.shot(x, y)) == value:
                results.append(screen)
        
        if len(results) != 1:
            return None

        return results[0]

    def shot(self) :
        if self.xy is None:
            return False
        
        self.np_value = self.capture.shot(self.xy[0], self.xy[1])[::-1, :, ::-1]
        return True

    def get_frame(self):
        if self.np_value is None:
            return None
        
        return self.np_value
    
    def is_black(self):
        return np.all(self.np_value == 0)

    def get_image(self):
        if self.np_value is None:
            return None
        
        return Image.fromarray(self.np_value)

    def get_resultscreen(self):
        now = datetime.now()
        filename = f'{now.strftime('%Y%m%d-%H%M%S-%f')}.png'

        return Screen(self.np_value, filename)

    def __del__(self):
        for screen, pos, capture, value in self.checkscreens:
            del capture
        del self.capture

class ThreadCapture(Thread):
    windottitle: str|None = None
    exename: str|None = None
    
    screenshot: Screenshot|None = None

    handle: int = 0
    active: bool = False
    waiting: bool = False
    musicselect: bool = False
    confirmed_loading: bool = False
    findtime_loading: float | None = None
    confirmed_somescreen: bool = False
    confirmed_processable: bool = False
    findtime_processable: float | None = None
    processed: bool = False
    screen_latest = None
    capturing_successful: bool | None = None
    '''キャプチャーの成否
    
    None: 評価が終わっていない
    True: キャプチャーできている
    False: キャプチャーできていない
    '''
    capturing_checkstarttime = None
    '''キャプチャーチェックの開始時間

    一定時間真っ暗が続いた場合はキャプチャー不可とする。
    '''

    event_close = Event()
    queue_message = Queue()
    queue_resultscreen = Queue(1)
    queue_musicselectscreen = Queue(1)

    collectionuploader: CollectionUploader|None
    setting: Setting|None

    def __init__(self, windowtitle: str, exename: str):
        self.windowtitle = windowtitle
        self.exename = exename

        self.screenshot = Screenshot()

        Thread.__init__(self)

    def run(self):
        self.sleep_time = thread_time_wait_nonactive
        logger.debug('start capture thread.')
        while not self.event_close.wait(timeout=self.sleep_time):
            self.routine()

    def routine(self):
        if self.handle == 0:
            self.handle = find_window(self.windowtitle, self.exename)
            if self.handle == 0:
                return

            logger.debug(f'infinitas find.')
            self.queue_message.put(('switch_detect_infinitas', True,))
            self.active = False
            self.screenshot.xy = None
        
        rect = get_rect(self.handle)

        if rect is None or rect.width == 0 or rect.height == 0:
            logger.debug(f'infinitas lost.')
            self.queue_message.put(('switch_detect_infinitas', False,))
            self.queue_message.put(('switch_capturable', False,))
            self.sleep_time = thread_time_wait_nonactive

            self.handle = 0
            self.active = False
            self.screenshot.xy = None

            return

        if not check_rectsize(rect):
            if self.active:
                self.sleep_time = thread_time_wait_nonactive
                logger.debug(f'infinitas deactivate: {self.sleep_time}')
                self.queue_message.put(('switch_capturable', False,))

            self.active = False
            self.screenshot.xy = None
            return
        
        if not self.active:
            self.active = True
            self.capturing_successful = None
            self.capturing_checkstarttime = time()
            self.waiting = False
            self.musicselect = False
            self.sleep_time = thread_time_normal
            logger.debug(f'infinitas activate: {self.sleep_time}')
            self.queue_message.put(('switch_capturable', True,))
        
        self.screenshot.xy = (rect.left, rect.top,)
        screen = self.screenshot.get_screen()

        shotted = False
        if self.capturing_successful is None:
            self.screenshot.shot()
            shotted = True

            if not self.screenshot.is_black():
                self.capturing_successful = True
            else:
                if time() - self.capturing_checkstarttime >= 60:
                    self.capturing_successful = False
                    messages = [
                        'キャプチャー画面がずっと真っ黒です。',
                        '',
                        'ゲーム実行ファイル(\\beatmania IIDX INFINITAS\\games\\app\\bm2dx.exe)のプロパティから「全画面表示の最適化を無効にする」のチェックを外すと正常化する可能性があります。',
                    ]
                    self.queue_message.put(('error', messages,))

        if not self.capturing_successful:
            return
        
        if screen != self.screen_latest:
            self.confirmed_somescreen = False
            self.confirmed_processable = False
            self.processed = False
            self.screen_latest = screen

        if screen == 'loading':
            if self.waiting:
                return
            
            if not self.confirmed_loading:
                self.confirmed_loading = True
                self.findtime_loading = time()
                return
            
            if time() - self.findtime_loading <= thread_time_normal * 2 - 0.1:
                return
            
            self.waiting = True
            self.musicselect = False
            self.sleep_time = thread_time_wait_loading
            logger.debug(f'detect loading: start waiting: {self.sleep_time}')
            self.queue_message.put(('detect_loading',))
            return
            
        self.confirmed_loading = False

        if self.waiting:
            self.waiting = False
            self.sleep_time = thread_time_normal
            logger.debug(f'escape loading: end waiting: {self.sleep_time}')
            self.queue_message.put(('escape_loading',))

        # ここから先はローディング中じゃないときのみ
        
        if screen != 'music_select' and self.musicselect:
            # 画面が選曲から抜けたとき
            self.musicselect = False
            self.sleep_time = thread_time_normal
            logger.debug(f'screen out music select: {self.sleep_time}')

        if screen == 'music_select':
            if not self.musicselect:
                # 画面が選曲に入ったとき
                self.musicselect = True
                self.sleep_time = thread_time_musicselect
                logger.debug(f'screen in music select: {self.sleep_time}')

            if not shotted:
                self.screenshot.shot()
                shotted = True

            trimmed = self.screenshot.np_value[define.musicselect_trimarea_np]
            playmode = recog.MusicSelect.get_playmode(trimmed)
            version = recog.MusicSelect.get_version(trimmed)
            if playmode is not None and version is not None:
                try:
                    image = self.screenshot.get_image()
                    self.queue_musicselectscreen.put((image, trimmed,), block=False)
                except Full as ex:
                    pass
            else:
                if self.setting.data_collection:
                    if recog.MusicSelect.get_hasscoredata(trimmed):
                        self.collectionuploader.musicselectchecker_reset()

            return

        if screen != 'result':
            self.confirmed_somescreen = False
            self.confirmed_processable = False
            self.processed = False

            if self.setting and self.setting.data_collection:
                if self.collectionuploader:
                    self.collectionuploader.notesradarchecker_reset()
            
            return
        
        # ここから先はリザルトのみ

        if not self.confirmed_somescreen:
            self.confirmed_somescreen = True

            # リザルトのときのみ、スレッド周期を短くして取込タイミングを高速化する
            self.sleep_time = thread_time_result
            logger.debug(f'screen in result: {self.sleep_time}')
        
        if self.processed and not self.setting and self.setting.data_collection:
            return
        
        if not self.processed:
            if not shotted:
                self.screenshot.shot()
            
            if not recog.get_is_savable(self.screenshot.np_value):
                return
            
            if not self.confirmed_processable:
                self.confirmed_processable = True
                self.findtime_processable = time()
                return

            if time() - self.findtime_processable <= thread_time_normal * 2 - 0.1:
                return

            resultscreen = self.screenshot.get_resultscreen()

            try:
                self.queue_resultscreen.put(resultscreen, block=False)
            except Full as ex:
                pass

            self.sleep_time = thread_time_normal
            logger.debug(f'processing result screen: {self.sleep_time}')
            self.processed = True
        
        if self.processed and self.setting and self.setting.data_collection:
            if self.collectionuploader:
                if not shotted:
                    self.screenshot.shot()
                
                self.collectionuploader.checkandupload_notesradarvalue(self.screenshot.np_value)
