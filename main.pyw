import keyboard
import time
import PySimpleGUI as sg
import threading
from queue import Queue
from os.path import join,exists
from PIL import Image
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
from resources import MusicsTimestamp,play_sound_find,play_sound_result,recog_musics_filepath
from screenshot import Screenshot
from recog import recog
from raw_image import save_raw
from storage import StorageAccessor
from record import Record
from graph import create_graph,save_graphimage
from result import results_basepath

thread_time_normal = 0.37
thread_time_wait = 2
thread_count_wait = int(30 / thread_time_wait)

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'

class ThreadMain(threading.Thread):
    positioned = False
    waiting = False
    waiting_count = 0
    finded = False
    processed = False
    logs = []

    def __init__(self, event_close, queues):
        self.event_close = event_close
        self.queues = queues

        threading.Thread.__init__(self)

        self.start()

    def run(self):
        self.sleep_time = thread_time_wait
        self.queues['log'].put('start thread')
        while not self.event_close.isSet():
            time.sleep(self.sleep_time)
            self.routine()

    def routine(self):
        screenshot.shot()

        if not self.positioned:
            if screenshot.find():
                self.positioned = True
                self.queues['log'].put(f'region = {screenshot.region}')
                self.sleep_time = thread_time_normal
                self.queues['log'].put(f'change sleep time: {self.sleep_time}')
                if setting.play_sound:
                    play_sound_find()

            return

        if self.waiting:
            self.waiting_count -= 1
            if self.waiting_count > 0:
                return
            
            if not screenshot.is_ended_waiting:
                self.waiting_count = thread_count_wait
                return

            self.waiting = False
            self.queues['log'].put('find playing: end waiting')
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'change sleep time: {self.sleep_time}')

        if screenshot.is_loading:
            self.finded = False
            self.processed = False
            self.waiting = True
            self.waiting_count = thread_count_wait
            self.queues['log'].put('find loading: start waiting')
            self.sleep_time = thread_time_wait
            self.queues['log'].put(f'change sleep time: {self.sleep_time}')
            return

        resultscreen = screenshot.get_resultscreen()
        if resultscreen is not None:
            if display_screenshot_enable:
                self.queues['display_image'].put(resultscreen.original)
            
            if not self.finded:
                self.finded = True
                self.find_time = time.time()
            if self.finded and not self.processed:
                if time.time() - self.find_time > thread_time_normal*2-0.1:
                    self.processed = True
                    self.queues['result_screen'].put(resultscreen)
                    if setting.play_sound:
                        play_sound_result()
        else:
            if self.finded:
                self.finded = False
                self.processed = False

class TargetRecord():
    def __init__(self, music, record, play_mode, difficulty, selected):
        self.music = music
        self.record = record
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.selected = selected

def result_process(screen):
    result = recog.get_result(screen)
    if setting.data_collection:
        storage.upload_collection(screen, result, window['force_upload'].get())
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
            window['table_results'].update(select_rows=[len(results)-1])
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
    screenshot.shot()
    screen = screenshot.get()
    filename = save_raw(screen)
    log_debug(f'save screen: {filename}')
    gui.display_image(screen)

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

def check_resource_musics():
    if setting.manage:
        return
    
    musics_timestamp = MusicsTimestamp()

    latest_timestamp = str(storage.get_resource_musics_timestamp())
    if latest_timestamp is None:
        return
    
    local_timestamp = musics_timestamp.get_timestamp()

    if local_timestamp != latest_timestamp:
        threading.Thread(target=download_resource_musics, args=(musics_timestamp, latest_timestamp)).start()

def download_resource_musics(musics_timestamp, latest_timestamp):
    if storage.download_resource_musics(recog_musics_filepath):
        musics_timestamp.write_timestamp(latest_timestamp)
        recog.load_resource_musics()
        print('download')

def select_result_today(selected_todayresults):
    if len(selected_todayresults) != 1:
        return None

    selected_todayresult = selected_todayresults[0]
    result = results[list_results[selected_todayresult][0]]

    return result

def load_record(result):
    informations = result.informations
    if informations.music is None:
        return None
    
    record = Record(informations.music)
    target_record = record.get(informations.play_mode, informations.difficulty)

    if target_record is None:
        return None

    selected_record = TargetRecord(
        informations.music,
        record,
        informations.play_mode,
        informations.difficulty,
        target_record
    )

    if informations.play_mode == 'SP':
        window['play_mode_sp'].update(True)
    if informations.play_mode == 'DP':
        window['play_mode_dp'].update(True)
    
    window['difficulty'].update(informations.difficulty)
    window['search_music'].update(informations.music)

    return selected_record

def select_music_search(selected_musics):
    if len(selected_musics) != 1:
        return None

    window['table_results'].update(select_rows=[])

    selected_music = selected_musics[0]
    record = Record(selected_music)

    if record is None:
        return None
    
    play_mode = None
    if window['play_mode_sp'].get():
        play_mode = 'SP'
    if window['play_mode_dp'].get():
        play_mode = 'DP'
    if play_mode is None:
        return None

    difficulty = window['difficulty'].get()
    if difficulty == '':
        return None

    target_record = record.get(play_mode, difficulty)
    if target_record is None:
        return None

    return TargetRecord(selected_music, record, play_mode, difficulty, target_record)

def select_history(selected_histories):
    if len(selected_histories) != 1:
        return
    
    selected_timestamp = selected_histories[0]
    filepath = join(results_basepath, f'{selected_timestamp}.jpg')
    if exists(filepath):
        image = Image.open(filepath)
        gui.display_image(image)
    else:
        gui.display_image(None)

    window['table_results'].update(select_rows=[])
    gui.display_historyresult(selected_record.selected, selected_timestamp)

if __name__ == '__main__':
    if setting.manage:
        keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = gui.generate_window(setting, version)

    display_screenshot_enable = False

    screenshot = Screenshot()

    results = {}
    list_results = []
    selected_result = None
    selected_record = None
    displaying_graphimage = None

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

    check_resource_musics()
    
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
        if event == 'check_play_sound':
            setting.play_sound = values['check_play_sound']
        if event == 'button_save':
            if selected_result is not None:
                save_result(selected_result)
            if displaying_graphimage is not None:
                save_graphimage(displaying_graphimage)
        if event == 'button_save_filtered' and selected_result is not None:
            ret = save_result_filtered(selected_result)
            if ret is not None:
                gui.display_image(ret, True, False)
        if event == 'table_results':
            selected_result = select_result_today(values['table_results'])
            if selected_result is not None:
                selected_record = load_record(selected_result)
                displaying_graphimage = None
                if selected_record is not None:
                    music_search_time = time.time() + 1
                    gui.display_record(selected_record.selected)
                else:
                    gui.display_record(None)
                gui.display_image(selected_result.image, True, True)
        if event == 'button_graph':
            if selected_record is not None:
                selected_result = None
                displaying_graphimage = create_graph(selected_record)
                gui.display_image(displaying_graphimage, savable=True)
        if event == 'search_music':
            music_search_time = time.time() + 1
        if event in ['play_mode_sp', 'play_mode_dp', 'difficulty', 'music_candidates']:
            selected_result = None
            selected_record = select_music_search(values['music_candidates'])
            if selected_record is not None:
                displaying_graphimage = create_graph(selected_record)
                gui.display_record(selected_record.selected)
                gui.display_image(displaying_graphimage, savable=True)
            else:
                displaying_graphimage = None
                gui.display_record(None)
                gui.display_image(None)
        if event == '選択した曲の記録を削除する':
            if selected_record is not None:
                selected_record.record.delete()
                gui.search_music_candidates()
            selected_record = None
            gui.display_record(None)
            gui.display_image(None)
        if event == 'history':
            select_history(values['history'])
        if event == '選択したリザルトの記録を削除する':
            if selected_record is not None:
                timestamp = select_history(values['history'])
                if timestamp is not None:
                    selected_record.record.delete_history(
                        selected_record.play_mode,
                        selected_record.difficulty,
                        timestamp
                    )
                    gui.display_record(selected_record.selected)
        if event == 'timeout':
            if not window['positioned'].visible and thread.positioned:
                window['positioned'].update(visible=True)
            if music_search_time is not None and time.time() > music_search_time:
                music_search_time = None
                gui.search_music_candidates()
            if not queue_log.empty():
                log_debug(queue_log.get_nowait())
            if not queue_display_image.empty():
                displaying_graphimage = None
                gui.display_image(queue_display_image.get_nowait())
            if not queue_result_screen.empty():
                ret = result_process(queue_result_screen.get_nowait())
                if ret is not None:
                    selected_result = ret
                    displaying_graphimage = None
    
    window.close()
