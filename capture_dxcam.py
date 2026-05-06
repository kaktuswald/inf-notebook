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
from dxcam import create as create_camera
from dxcam import DXCamera,Device,Output,enum_dxgi_adapters
from windows import get_monitorhandle

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

class Screenshot:
    camera: DXCamera|None = None
    frame: np.ndarray = None

    def __init__(self):
        self.checkscreens = []
        for screenname, item in resource.screenrecognition['get_screen'].items():
            self.checkscreens.append((
                screenname,
                (
                    slice(item['area']['top'], item['area']['top']+item['area']['height']),
                    slice(item['area']['left'], item['area']['left']+item['area']['width']),
                ),
                item['value'],
            ))
        
        return

    def create_camera(self, handle:int|None) -> bool:
        if not handle:
            return False

        mhandle = get_monitorhandle(handle)

        for i_adapter, p_adapter in enumerate(enum_dxgi_adapters()):
            device = Device(p_adapter)
            for i_output, p_output in enumerate(device.enum_outputs()):
                output = Output(p_output)
                output.hmonitor
                output.devicename
                if output.hmonitor == mhandle:
                    self.camera = create_camera(
                        device_idx=i_adapter,
                        output_idx=i_output,
                        processor_backend='numpy',
                    )
                    self.camera.start()

                    return True
        
        return False

    def clear_camera(self):
        if self.camera is None:
            return
        
        self.camera.stop()

        del self.camera
        self.camera = None
    
    def shot(self) -> bool:
        if self.camera is None:
            return False
        
        self.frame = self.camera.grab()

        return self.frame is not None

    def get_frame(self) -> np.ndarray:
        if self.frame is None:
            return None
        
        return self.frame
    
    def is_black(self) -> bool:
        return bool(np.all(self.frame == 0))

    def get_screen(self) -> str|None:
        if self.frame is None:
            return None
        
        results = []
        for screen, sl, value in self.checkscreens:
            if np.sum(self.frame[sl]) == value:
                results.append(screen)
        
        if len(results) != 1:
            return None
        
        return results[0]

    def get_image(self) -> Image.Image:
        if self.frame is None:
            return None
        
        return Image.fromarray(self.frame)

    def get_resultscreen(self) -> Screen:
        now = datetime.now()
        filename = f'{now.strftime('%Y%m%d-%H%M%S-%f')}.png'

        return Screen(self.frame, filename)
    
    @property
    def is_active(self) -> bool:
        return self.camera is not None

class ThreadCapture(Thread):
    windottitle: str|None = None
    exename: str|None = None

    screenshot: Screenshot|None = None

    handle: int = 0
    waiting: bool = False
    musicselect: bool = False
    confirmed_loading: bool = False
    findtime_loading: float | None = None
    confirmed_somescreen: bool = False
    confirmed_processable: bool = False
    findtime_processable: float | None = None
    processed: bool = False
    screen_latest = None

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
            self.screenshot.clear_camera()
        
        rect = get_rect(self.handle)

        if rect is None or rect.width == 0 or rect.height == 0:
            logger.debug(f'infinitas lost.')
            self.queue_message.put(('switch_detect_infinitas', False,))
            self.queue_message.put(('switch_capturable', False,))
            self.sleep_time = thread_time_wait_nonactive

            self.handle = 0
            self.screenshot.clear_camera()

            return

        if not check_rectsize(rect):
            if self.screenshot.is_active:
                self.sleep_time = thread_time_wait_nonactive
                logger.debug(f'infinitas deactivate: {self.sleep_time}')
                self.queue_message.put(('switch_capturable', False,))
                self.screenshot.clear_camera()
            
            return
        
        if not self.screenshot.is_active:
            self.waiting = False
            self.musicselect = False
            self.sleep_time = thread_time_normal
            logger.debug(f'infinitas activate: {self.sleep_time}')
            self.queue_message.put(('switch_capturable', True,))

            self.screenshot.create_camera(self.handle)
        
        self.screenshot.shot()

        screen = self.screenshot.get_screen()

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

            trimmed = self.screenshot.frame[define.musicselect_trimarea_np]
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
            if not recog.get_is_savable(self.screenshot.frame):
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
                self.collectionuploader.checkandupload_notesradarvalue(self.screenshot.frame)
