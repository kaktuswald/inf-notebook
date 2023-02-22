import keyboard
import time
import PySimpleGUI as sg
import threading
from queue import Queue
from os import system,getcwd
from os.path import join
import webbrowser
import logging
from urllib import request
from urllib.parse import quote

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
from graph import create_graph,save_graphimage,graphs_basepath
from result import get_resultimage,results_basepath,filterd_basepath

thread_time_normal = 0.37
thread_time_wait = 2
thread_count_wait = int(30 / thread_time_wait)

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'
tweet_url = 'https://twitter.com/intent/tweet'

tweet_template = '\n'.join((
    '&&music&&[&&play_mode&&&&D&&]',
    '#IIDX #infinitas573',
))

results_dirpath = join(getcwd(), results_basepath)
filtereds_dirpath = join(getcwd(), filterd_basepath)
graphs_dirpath = join(getcwd(), graphs_basepath)

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

class ActiveTarget():
    RESULT = 'result'
    FILTERED_RESULT = 'filtered_result'
    GRAPH = 'graph'
    result = None
    image_result = None
    image_filtered = None
    image_graph = None
    image_type = None

    def __init__(self, play_mode, difficulty, music, record):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.music = music
        self.record = record
    
    def get_targetrecord(self):
        return self.record.get(self.play_mode, self.difficulty)

def result_process(screen):
    result = recog.get_result(screen)
    if setting.data_collection:
        storage.upload_collection(screen, result, window['force_upload'].get())
    
    if setting.newrecord_only and not result.has_new_record():
        return None
    
    image = result.image

    if setting.autosave:
        save_result(result)
    
    if setting.autosave_filtered:
        filtered_image = save_result_filtered(result)
    else:
        filtered_image = None
    
    insert_results(result)

    music = result.informations.music
    record = Record(music) if music is not None else None

    if record is not None and (not result.dead or result.has_new_record()):
        record.insert(result)
        record.save()

    if not setting.display_result:
        return None

    play_mode = result.informations.play_mode,
    difficulty = result.informations.difficulty
    ret = ActiveTarget(play_mode, difficulty, music, record)

    ret.result = result
    ret.image_result = image
    if filtered_image is not None:
        ret.image_filtered = filtered_image
    ret.image_type = ret.RESULT

    gui.display_image(image, True, True)
    window['table_results'].update(select_rows=[len(results)-1])
    
    return ret

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

def tweet(target):
    text = tweet_template
    text = text.replace('&&play_mode&&', target.play_mode)
    if target.music is not None:
        text = text.replace('&&music&&', target.music)
    else:
        text = text.replace('&&music&&', '?????')
    text = text.replace('&&D&&', target.difficulty[0])
    text = quote(text)
    url = f'{tweet_url}?text={text}'
    webbrowser.open(url)

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

    gui.display_image(result.image, True, True)

    music = result.informations.music
    record = Record(music) if music is not None else None

    play_mode = result.informations.play_mode
    difficulty = result.informations.difficulty
    ret = ActiveTarget(play_mode, difficulty, music, record)
    ret.result = result
    ret.image_result = result.image
    ret.image_type = ret.RESULT
    if result.filtered is not None:
        ret.image_filtered = result.filtered
    
    if record is not None:
        if play_mode == 'SP':
            window['play_mode_sp'].update(True)
        if play_mode == 'DP':
            window['play_mode_dp'].update(True)
        
        window['difficulty'].update(difficulty)
        window['search_music'].update(music)

        gui.display_record(record.get(play_mode, difficulty))
    else:
        gui.display_record(None)

    return ret

def select_music_search(selected_musics):
    if len(selected_musics) != 1:
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

    window['table_results'].update(select_rows=[])

    music = selected_musics[0]
    record = Record(music)

    target_record = record.get(play_mode, difficulty)
    if target_record is None:
        return None

    return ActiveTarget(play_mode, difficulty, music, record)

def get_selecttimestamp(selected_histories):
    if len(selected_histories) != 1:
        return
    
    return selected_histories[0]

if __name__ == '__main__':
    if setting.manage:
        keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = gui.generate_window(setting, version)

    display_screenshot_enable = False

    screenshot = Screenshot()

    results = {}
    list_results = []
    activetarget = None

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

        try:
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
                if activetarget.image_type == activetarget.RESULT:
                    save_result(activetarget.result)
                if activetarget.image_type == activetarget.GRAPH:
                    save_graphimage(activetarget.image_graph)
            if event == 'button_save_filtered':
                if activetarget.image_filtered is None:
                    save_result_filtered(activetarget.result)
                    activetarget.image_filtered = activetarget.result.filtered
                activetarget.image_type = activetarget.FILTERED_RESULT
                gui.display_image(activetarget.image_filtered, True, False)
            if event == 'button_tweet':
                tweet(activetarget)
            if event == 'button_open_folder':
                if activetarget.image_type == activetarget.RESULT:
                    system(f'explorer.exe {results_dirpath}')
                if activetarget.image_type == activetarget.FILTERED_RESULT:
                    system(f'explorer.exe {filtereds_dirpath}')
                if activetarget.image_type == activetarget.GRAPH:
                    system(f'explorer.exe {graphs_dirpath}')
            if event == 'table_results':
                target = select_result_today(values['table_results'])
                if target is not None:
                    activetarget = target
                    if activetarget.music is not None:
                        music_search_time = time.time() + 1
            if event == 'button_graph':
                if activetarget is not None and activetarget.music is not None:
                    if activetarget.image_graph is None:
                        target_record = activetarget.get_targetrecord()
                        activetarget.image_graph = create_graph(
                            activetarget.play_mode,
                            activetarget.difficulty,
                            activetarget.music,
                            target_record
                        )
                    activetarget.image_type = activetarget.GRAPH
                    gui.display_image(activetarget.image_graph, savable=True)
            if event == 'search_music':
                music_search_time = time.time() + 1
            if event in ['play_mode_sp', 'play_mode_dp', 'difficulty', 'music_candidates']:
                activetarget = select_music_search(values['music_candidates'])
                if activetarget is not None:
                    target_record = activetarget.get_targetrecord()
                    activetarget.image_graph = create_graph(
                        activetarget.play_mode,
                        activetarget.difficulty,
                        activetarget.music,
                        target_record
                    )
                    activetarget.image_type = activetarget.GRAPH
                    gui.display_record(target_record)
                    gui.display_image(activetarget.image_graph, savable=True)
                else:
                    gui.display_record(None)
                    gui.display_image(None)
            if event == '選択した曲の記録を削除する':
                if activetarget is not None:
                    activetarget.record.delete()
                    activetarget = None
                    gui.search_music_candidates()
                gui.display_record(None)
                gui.display_image(None)
            if event == 'history':
                timestamp = get_selecttimestamp(values['history'])
                if timestamp is not None:
                    gui.display_historyresult(activetarget.get_targetrecord(), timestamp)
                    resultimage = get_resultimage(timestamp)
                    if resultimage is not None:
                        activetarget.image_result = resultimage
                        activetarget.image_type = activetarget.RESULT
                        gui.display_image(resultimage, False, False)
            if event == '選択したリザルトの記録を削除する':
                timestamp = get_selecttimestamp(values['history'])
                if timestamp is not None:
                    activetarget.record.delete_history(
                        activetarget.play_mode,
                        activetarget.difficulty,
                        timestamp
                    )
                    displaying_resultimage = None
                    gui.display_record(activetarget.get_targetrecord())
                    gui.display_image(None)
            if event == 'timeout':
                if not window['positioned'].visible and thread.positioned:
                    window['positioned'].update(visible=True)
                if music_search_time is not None and time.time() > music_search_time:
                    music_search_time = None
                    gui.search_music_candidates()
                if not queue_log.empty():
                    log_debug(queue_log.get_nowait())
                if not queue_display_image.empty():
                    activetarget = None
                    gui.display_image(queue_display_image.get_nowait())
                if not queue_result_screen.empty():
                    ret = result_process(queue_result_screen.get_nowait())
                    if ret is not None:
                        activetarget = ret
        except Exception as ex:
            log_debug(ex)
    
    window.close()
