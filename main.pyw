import keyboard
import time
import PySimpleGUI as sg
import threading
from queue import Queue
import os
import logging

from setting import Setting

setting = Setting()

if setting.manage:
    logging_level = logging.DEBUG
else:
    logging_level = logging.WARNING

logging.basicConfig(
    level=logging_level,
    filename='log.txt',
    filemode='w',
    format='%(asctime)s - %(name)s %(levelname)-7s %(message)s'
)

logger = logging.getLogger()

logger.debug('loaded main.py')
logger.debug('mode: manage')

from gui.main import generate_window,error_message,collection_request,display_image
from resources import finds
from screenshot import Screenshot
from recog import recog
from larning import save_raw
from storage import StorageAccessor

thread_time_start = 1
thread_time_normal = 0.35
thread_time_wait = 5

class ThreadMain(threading.Thread):
    positioned = False
    waiting = False
    finded = False
    processed = False
    logs = []

    def __init__(self, event_close, queues):
        self.event_close = event_close
        self.queues = queues

        threading.Thread.__init__(self)

        self.start()

    def run(self):
        self.sleep_time = thread_time_start
        self.queues['log'].put('start thread')
        while not self.event_close.isSet():
            time.sleep(self.sleep_time)
            self.routine()

    def routine(self):
        if not self.positioned:
            for key, target in finds.items():
                box = screenshot.find(target['image'])
                if not box is None:
                    self.positioned = True
                    self.queues['log'].put(f'find window: {key}')
                    self.queues['log'].put(f'position: {box}')
                    left = box.left - target['area'][0]
                    top = box.top - target['area'][1]
                    screenshot.region = (
                        left,
                        top,
                        left + screenshot.width,
                        top + screenshot.height
                    )
                    self.queues['log'].put(f'region = {screenshot.region}')
                    self.sleep_time = thread_time_normal
                    self.queues['log'].put(f'change sleep time: {self.sleep_time}')
                    break
            return

        screen = screenshot.shot()
        if display_screenshot_enable:
            self.queues['display_image'].put(screen.original)
        
        starting = recog.get_starting(screen.image)
        if not self.waiting and starting == 'loading':
            self.finded = False
            self.processed = False
            self.waiting = True
            self.queues['log'].put('find loading: start waiting')
            self.sleep_time = thread_time_wait
            self.queues['log'].put(f'change sleep time: {self.sleep_time}')
        if self.waiting and starting == 'warning':
            self.waiting = False
            self.queues['log'].put('find warning: end waiting')
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'change sleep time: {self.sleep_time}')

        if not self.waiting:
            if recog.is_result(screen.image):
                if not self.finded:
                    self.finded = True
                    self.find_time = time.time()
                if self.finded and not self.processed:
                    if time.time() - self.find_time > thread_time_normal*2-0.1:
                        self.processed = True
                        self.queues['result_screen'].put(screen)
            else:
                if self.finded:
                    self.finded = False
                    self.processed = False

def result_process(screen):
    result = recog.get_result(screen)
    if setting.data_collection:
        storage.upload_collection(screen, result)
    if not setting.save_newrecord_only or result.hasNewRecord():
        try:
            result.save()
        except Exception as ex:
            logger.exception(ex)
            error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
            return
        
        log_debug(f'save result: {result.filename}')
        insert_results(result)
        if setting.display_saved_result:
            display_image(result.original)

def insert_results(result):
    results[result.filename] = result
    list_results.append([
        result.filename,
        '☑' if result.details['clear_type_new'] else '',
        '☑' if result.details['dj_level_new'] else '',
        '☑' if result.details['score_new'] else '',
        '☑' if result.details['miss_count_new'] else ''
    ])
    window['table_results'].update(values=list_results)

def active_screenshot():
    screen = screenshot.shot()
    save_raw(screen)
    log_debug(f'save screen: {screen.filename}')
    display_image(screen.original)

def log_debug(message):
    logger.debug(message)
    if setting.manage:
        print(message)

if __name__ == '__main__':
    if setting.manage:
        keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = generate_window(setting)

    display_screenshot_enable = False

    screenshot = Screenshot()

    result = None
    results = {}
    list_results = []

    queue_log = Queue()
    queue_display_image = Queue()
    queue_result_screen = Queue()

    storage = StorageAccessor()

    event_close = threading.Event()
    thread = ThreadMain(
        event_close,
        queues = {
            'log': queue_log,
            'display_image': queue_display_image,
            'result_screen': queue_result_screen
        }
    )

    if not setting.has_key('data_collection'):
        setting.data_collection = collection_request('resources/annotation.png')

    while True:
        event, values = window.read(timeout=50, timeout_key='timeout')

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            if not thread is None:
                event_close.set()
                thread.join()
                log_debug(f'end')
            break
        if event == 'check_display_screenshot':
            display_screenshot_enable = values['check_display_screenshot']
        if event == 'check_display_saved_result':
            setting.display_saved_result = values['check_display_saved_result']
        if event == 'check_save_newrecord_only':
            setting.save_newrecord_only = values['check_save_newrecord_only']
        if event == 'text_file_path':
            if os.path.exists(values['text_file_path']):
                screen = screenshot.open(values['text_file_path'])
                display_image(screen.original)
                if recog.is_result(screen.image):
                    result_process(screen)
        if event == 'button_filter' and result is not None:
            try:
                filtered = result.filter()
            except Exception as ex:
                logger.exception(ex)
                error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
                continue
            display_image(filtered)
            log_debug(f'save filtered result: {result.filename}')
        if event == 'table_results':
            if len(values['table_results']) > 0:
                result = results[list_results[values['table_results'][0]][0]]
                display_image(result.image)
        if event == 'timeout':
            if not queue_log.empty():
                log_debug(queue_log.get_nowait())
            if not queue_display_image.empty():
                display_image(queue_display_image.get_nowait())
            if not queue_result_screen.empty():
                result_process(queue_result_screen.get_nowait())
    
    window.close()
