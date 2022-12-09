import keyboard
import time
import PySimpleGUI as sg
import threading
from queue import Queue
import io
import logging
import PySimpleGUI as pgui

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

from gui.main import layout_main
from resources import finds
from screenshot import Screenshot
from recog import recog
from larning import create_larning_source_directory,save_larning_source
from storage import StorageAccessor

screenshot = Screenshot()

thread_time_start = 1
thread_time_normal = 0.35
thread_time_wait = 5

display_screenshot_enable = False

results = {}
list_results = []

storage = StorageAccessor()

class MyThread(threading.Thread):
    positioned = False
    waiting = False
    finded = False
    processed = False
    logs = []

    def __init__(self, event_close, queue_log, queue_image, queue_result):
        self.event_close = event_close
        self.queue_log = queue_log
        self.queue_image = queue_image
        self.queue_result = queue_result

        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.sleep_time = thread_time_start
        self.queue_log.put('start thread')
        while not self.event_close.isSet():
            time.sleep(self.sleep_time)
            self.routine()

    def routine(self):
        if not self.positioned:
            for key, target in finds.items():
                box = screenshot.find(target['image'])
                if not box is None:
                    self.positioned = True
                    self.queue_log.put(f'find window: {key}')
                    self.queue_log.put(f'position: {box}')
                    left = box.left - target['area'][0]
                    top = box.top - target['area'][1]
                    screenshot.region = (
                        left,
                        top,
                        left + screenshot.width,
                        top + screenshot.height
                    )
                    self.queue_log.put(f'region = {screenshot.region}')
                    self.sleep_time = thread_time_normal
                    self.queue_log.put(f'change sleep time: {self.sleep_time}')
                    break
            return

        screen = screenshot.shot()
        if display_screenshot_enable:
            self.queue_image.put(screen.original)
        
        starting = recog.get_starting(screen.image)
        if not self.waiting and starting == 'recognized loading':
            self.finded = False
            self.processed = False
            self.waiting = True
            self.queue_log.put('find loading: start waiting')
            self.sleep_time = thread_time_wait
            self.queue_log.put(f'change sleep time: {self.sleep_time}')
        if self.waiting and starting == 'recognized warning':
            self.waiting = False
            self.queue_log.put('find warning: end waiting')
            self.sleep_time = thread_time_normal
            self.queue_log.put(f'change sleep time: {self.sleep_time}')

        if not self.waiting:
            if recog.is_result(screen.image):
                if not self.finded:
                    self.finded = True
                    self.find_time = time.time()
                if self.finded and not self.processed:
                    if time.time() - self.find_time > thread_time_normal*2-0.1:
                        self.processed = True
                        if setting.manage:
                            save_larning_source(screen)
                        result = result_process(screen)
                        if result is not None:
                            self.queue_result.put(result)
                            if setting.display_saved_result:
                                self.queue_image.put(screen.original)
            else:
                if self.finded:
                    self.finded = False
                    self.processed = False

def result_process(screen):
    result = recog.get_result(screen)
    if setting.data_collection:
        storage.upload_collection(screen, result)
    if not setting.save_newrecord_only or result.hasNewRecord():
        result.save()
        logger.debug(f'save: {result.filename}')
        return result
    
    return None

def insert_results(result):
    if not result.filename in results.keys():
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
    save_larning_source(screen)
    logger.debug(f'save: {screen.filename}')
    if display_screenshot_enable:
        display_image(screen.original)

def display_image(image):
    scale = window['scale'].get()
    if scale == '1/2':
        image = image.resize((image.width // 2, image.height // 2))
    if scale == '1/4':
        image = image.resize((image.width // 3, image.height // 3))
    
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')

    window['screenshot'].update(size=image.size, data=bytes.getvalue())

if __name__ == '__main__':
    if setting.manage:
        create_larning_source_directory()
        keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = sg.Window(
        'beatmaniaIIDX INFINITAS リザルト手帳',
        layout_main(setting),
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True
    )

    queue_log = Queue()
    queue_image = Queue()
    queue_result = Queue()

    event_close = threading.Event()
    thread = MyThread(event_close, queue_log, queue_image, queue_result)

    if not setting.has_key('data_collection'):
        ret = pgui.popup_yes_no(
            '\n'.join([
                '画像処理の精度向上のために大量のリザルト画像を欲しています。',
                'リザルト画像を上画像のように切り取ってクラウドにアップロードします。',
                'もちろん、他の目的に使用することはしません。'
                '\n',
                '実現できるかどうかはわかりませんが、',
                '曲名を含めてあらゆる情報を画像から抽出して',
                '過去のリザルトの検索などできるようにしたいと考えています。'
            ]),
            title='おねがい',
            image='resources/annotation.png'
        )

        setting.data_collection = True if ret == 'Yes' else False

    while True:
        event, values = window.read(timeout=50, timeout_key='timeout')

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            if not thread is None:
                event_close.set()
                thread.join()
                logger.debug(f'end')
            break
        if event == 'check_display_screenshot':
            display_screenshot_enable = values['check_display_screenshot']
        if event == 'check_display_saved_result':
            setting.display_saved_result = values['check_display_saved_result']
        if event == 'check_save_newrecord_only':
            setting.save_newrecord_only = values['check_save_newrecord_only']
        if event == 'text_file_path':
            screen = screenshot.open(values['text_file_path'])
            display_image(screen.original)
            if recog.is_result(screen.image):
                result = result_process(screen)
                if result is not None:
                    insert_results(result)
        if event == 'button_filter' and not result is None:
            ret = result.filter()
            if not ret is None:
                display_image(ret)
        if event == 'table_results':
            if len(values['table_results']) > 0:
                result = results[list_results[values['table_results'][0]][0]]
                display_image(result.image)
        if event == 'timeout':
            if not queue_log.empty():
                logger.debug(queue_log.get_nowait())
            if not queue_result.empty():
                insert_results(queue_result.get_nowait())
            if not queue_image.empty():
                display_image(queue_image.get_nowait())
    
    window.close()
