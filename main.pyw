import keyboard
import time
import PySimpleGUI as sg
import threading
from queue import Queue
import os
import logging
from urllib import request

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

from version import version
import gui.main as gui
from define import define
from resources import find_images
from screenshot import Screenshot
from recog import recog
from raw_image import save_raw
from storage import StorageAccessor
from record import Record

thread_time_start = 2
thread_time_normal = 0.37
thread_time_wait = 30

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'

class ThreadMain(threading.Thread):
    positioned = False
    waiting = False
    finded = False
    processed = False
    logs = []

    def __init__(self, event_close, queues):
        self.event_close = event_close
        self.queues = queues
        self.screen_search_keyindex = 0

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
            key = [*define.screen_areas.keys()][self.screen_search_keyindex]
            box = screenshot.find(find_images[key])

            if not box is None:
                self.positioned = True
                self.queues['log'].put(f'find window: {key}')
                self.queues['log'].put(f'position: {box}')
                left = box.left - define.screen_areas[key][0]
                top = box.top - define.screen_areas[key][1]
                screenshot.region = (
                    left,
                    top,
                    left + screenshot.width,
                    top + screenshot.height
                )
                self.queues['log'].put(f'region = {screenshot.region}')
                self.sleep_time = thread_time_normal
                self.queues['log'].put(f'change sleep time: {self.sleep_time}')

            self.screen_search_keyindex = (self.screen_search_keyindex + 1) % len(define.screen_areas.keys())
            return

        screen = screenshot.shot()
        if display_screenshot_enable:
            self.queues['display_image'].put(screen.original)
        
        if self.waiting:
            if not recog.is_ended_waiting(screen.image):
                return

            self.waiting = False
            self.queues['log'].put('find playing: end waiting')
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'change sleep time: {self.sleep_time}')

        if recog.search_loading(screen.image):
            self.finded = False
            self.processed = False
            self.waiting = True
            self.queues['log'].put('find loading: start waiting')
            self.sleep_time = thread_time_wait
            self.queues['log'].put(f'change sleep time: {self.sleep_time}')
            return

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
    if not setting.newrecord_only or result.has_new_record():
        image = result.image
        if setting.autosave:
            save_result(result)
        if setting.autosave_filtered:
            image = save_result_filtered(result)
        
        insert_results(result)

        if result.informations.music is not None and (not result.dead or result.has_new_record()):
            record = Record(result.informations.music)
            record.insert(result)
            record.save()

        if setting.display_result and image is not None:
            gui.display_image(image, True)
            return result

    return None

def save_result(result):
    try:
        result.save()
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    log_debug(f'save result: {result.timestamp}.jpg')

def save_result_filtered(result):
    try:
        filtered = result.filter()
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return None

    log_debug(f'save filtered result: {result.timestamp}.jpg')
    return filtered

def insert_results(result):
    results[result.timestamp] = result

    play_mode = result.informations.play_mode
    difficulty = result.informations.difficulty
    music = result.informations.music

    list_results.append([
        result.timestamp,
        music if music is not None else '??????',
        f'{play_mode}{difficulty[0]}' if play_mode is not None and difficulty is not None else '???',
        '☑' if result.details.clear_type.new else '',
        '☑' if result.details.dj_level.new else '',
        '☑' if result.details.score.new else '',
        '☑' if result.details.miss_count.new else ''
    ])
    window['table_results'].update(values=list_results)

def active_screenshot():
    screen = screenshot.shot()
    save_raw(screen)
    log_debug(f'save screen: {screen.filename}')
    gui.display_image(screen.original)

def log_debug(message):
    logger.debug(message)
    if setting.manage:
        print(message)

def get_latest_version():
    with request.urlopen(latest_url) as response:
        url = response.geturl()
        version = url.split('/')[-1]
        print(f'released latest version: {version}')
        if version[0] == 'v':
            return version.replace('v', '')
        else:
            return None

if __name__ == '__main__':
    if setting.manage:
        keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = gui.generate_window(setting, version)

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

    music_search_time = None

    if not setting.has_key('data_collection'):
        setting.data_collection = gui.collection_request('resources/annotation.png')

    if version != '0.0.0.0' and get_latest_version() != version:
        gui.find_latest_version(latest_url)

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
        if event == 'check_display_result':
            setting.display_result = values['check_display_result']
        if event == 'check_newrecord_only':
            setting.newrecord_only = values['check_newrecord_only']
        if event == 'check_autosave':
            setting.autosave = values['check_autosave']
        if event == 'check_autosave_filtered':
            setting.autosave_filtered = values['check_autosave_filtered']
        if event == 'check_display_music':
            setting.display_music = values['check_display_music']
            gui.switch_table(setting.display_music)
        if event == 'text_file_path':
            if os.path.exists(values['text_file_path']):
                screen = screenshot.open(values['text_file_path'])
                gui.display_image(screen.original)
                if recog.is_result(screen.image):
                    result_process(screen)
        if event == 'button_save' and result is not None:
            save_result(result)
        if event == 'button_save_filtered' and result is not None:
            ret = save_result_filtered(result)
            if ret is not None:
                gui.display_image(ret, True)
        if event == 'table_results':
            if len(values['table_results']) > 0:
                result = results[list_results[values['table_results'][0]][0]]
                gui.display_image(result.image, True)
        if event == 'search_music':
            music_search_time = time.time() + 1
        if event == 'play_mode_sp':
            gui.select_music()
        if event == 'play_mode_dp':
            gui.select_music()
        if event == 'difficulty':
            gui.select_music()
        if event == 'music_candidates':
            gui.select_music()
        if event == 'history':
            gui.select_history()
        if event == 'timeout':
            if music_search_time is not None and time.time() > music_search_time:
                music_search_time = None
                gui.search_music_candidates()
            if not queue_log.empty():
                log_debug(queue_log.get_nowait())
            if not queue_display_image.empty():
                gui.display_image(queue_display_image.get_nowait())
            if not queue_result_screen.empty():
                ret = result_process(queue_result_screen.get_nowait())
                if ret is not None:
                    result = ret
    
    window.close()
