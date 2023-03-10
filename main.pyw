import keyboard
import time
import PySimpleGUI as sg
import threading
from queue import Queue
from os import system,getcwd
from os.path import join,exists
import webbrowser
import logging
from urllib import request
from urllib.parse import quote
import pygetwindow as gw

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
from gui.general import get_imagevalue
from resources import MusicsTimestamp,play_sound_find,play_sound_result,recog_musics_filepath
from screenshot import Screenshot,open_screenimage
from recog import recog
from raw_image import save_raw
from storage import StorageAccessor
from record import Record
from graph import create_graphimage,save_graphimage,graphs_basepath
from result import get_resultimagevalue,get_filteredimagevalue,results_basepath,filtereds_basepath

thread_time_normal = 0.37
thread_time_wait = 2
thread_count_wait = int(30 / thread_time_wait)

title = 'beatmaniaIIDX INFINITAS'

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'
tweet_url = 'https://twitter.com/intent/tweet'

tweet_template_music = '&&music&&[&&play_mode&&&&D&&]'
tweet_template_hashtag = '#IIDX #infinitas573 #infnotebook'

results_dirpath = join(getcwd(), results_basepath)
filtereds_dirpath = join(getcwd(), filtereds_basepath)
graphs_dirpath = join(getcwd(), graphs_basepath)

class ThreadMain(threading.Thread):
    window = None
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
        while not self.event_close.is_set():
            time.sleep(self.sleep_time)
            self.routine()

    def routine(self):
        global screenshot
        if screenshot is None:
            find_windows = gw.getWindowsWithTitle(title)
            if len(find_windows) != 1:
                return

            window = find_windows[0]
            if window.title != title:
                return

            self.window = window
            area = [*window.topleft, window.left+window.width, window.top+window.height]
            screenshot = Screenshot(area)
            play_sound_find()

        if not self.window.title in gw.getAllTitles():
            self.window = None
            screenshot = None
            return
        
        screenshot.shot()

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

class Selection():
    def __init__(self, play_mode, difficulty, music, record):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.music = music
        self.record = record
        self.today = False
        self.filtered = False
        self.graph = False
        self.timestamp = None
    
    def selection_today(self, result):
        self.today = True
        self.filtered = False
        self.graph = False
        self.timestamp = result.timestamp

    def selection_graph(self):
        if self.music is None:
            return False
        
        self.today = False
        self.filtered = False
        self.graph = True
        self.timestamp = None

        return True

    def selection_timestamp(self, timestamp):
        self.today = False
        self.filtered = False
        self.graph = False
        self.timestamp = timestamp
    
    def selection_filtered(self):
        self.filtered = True
        self.graph = False

    def get_targetrecord(self):
        return self.record.get(self.play_mode, self.difficulty)

def result_process(screen):
    result = recog.get_result(screen)
    if setting.data_collection:
        storage.upload_collection(screen, result, window['force_upload'].get())
    
    if setting.newrecord_only and not result.has_new_record():
        return None
    
    if setting.autosave:
        save_result(result)
    
    if setting.autosave_filtered:
        result.filter()
        save_filtered(result)
    
    music = result.informations.music
    if music is not None:
        if music in records.keys():
            record = records[music]
        else:
            record = Record(music) if music is not None else None
            records[music] = record

        if not result.dead or result.has_new_record():
            record.insert(result)
            record.save()

    insert_results(result)

    if setting.display_result:
        window['table_results'].update(select_rows=[len(results)-1])
        return None

def save_result(result):
    try:
        ret = result.save()
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        log_debug(f'save result: {result.timestamp}.jpg')

def save_filtered(result):
    try:
        ret = result.save_filtered()
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        log_debug(f'save filtered result: {result.timestamp}.jpg')

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
    gui.display_image(get_imagevalue(screen))

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
            return version.removeprefix('v')
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

def select_result_today():
    if len(values['table_results']) != 1:
        return None

    window['music_candidates'].update(set_to_index=[])

    result = results[list_results[values['table_results'][0]][0]]

    if result.timestamp in imagevalues_result:
        imagevalue = imagevalues_result[result.timestamp]
    else:
        imagevalue = get_imagevalue(result.image)
        imagevalues_result[result.timestamp] = imagevalue
    gui.display_image(imagevalue, not result.saved, True)

    music = result.informations.music

    ret = Selection(
        result.informations.play_mode,
        result.informations.difficulty,
        result.informations.music,
        records[music] if music is not None else None
    )
    ret.selection_today(result)
    
    if ret.record is not None:
        if ret.play_mode == 'SP':
            window['play_mode_sp'].update(True)
        if ret.play_mode == 'DP':
            window['play_mode_dp'].update(True)
        
        window['difficulty'].update(ret.difficulty)
        window['search_music'].update(music)

        gui.display_record(ret.get_targetrecord())
    else:
        gui.display_record(None)

    return ret

def select_music_search():
    if len(values['music_candidates']) != 1:
        return None

    play_mode = None
    if values['play_mode_sp']:
        play_mode = 'SP'
    if values['play_mode_dp']:
        play_mode = 'DP'
    if play_mode is None:
        return None

    difficulty = values['difficulty']
    if difficulty == '':
        return None

    music = values['music_candidates'][0]

    window['table_results'].update(select_rows=[])

    if music in records.keys():
        record = records[music]
    else:
        record = Record(music)
        records[music] = record

    if record.get(play_mode, difficulty) is None:
        gui.display_record(None)
        gui.display_image(None)
        return None

    ret = Selection(play_mode, difficulty, music, record)
    targetrecord = ret.record.get(play_mode, difficulty)

    gui.display_record(targetrecord)
    create_graph(ret, targetrecord)

    return ret

def select_timestamp():
    if len(values['history']) != 1:
        return
    
    window['table_results'].update(select_rows=[])

    timestamp = values['history'][0]
    selection.selection_timestamp(timestamp)

    gui.display_historyresult(selection.get_targetrecord(), timestamp)

    if timestamp in imagevalues_result.keys():
        resultimage = imagevalues_result[timestamp]
    else:
        resultimage = get_resultimagevalue(timestamp)
        imagevalues_result[timestamp] = resultimage

    if timestamp in imagevalues_filtered.keys():
        filteredimage = imagevalues_filtered[timestamp]
    else:
        filteredimage = get_filteredimagevalue(timestamp)
        imagevalues_filtered[timestamp] = filteredimage

    if resultimage is not None:
        gui.display_image(resultimage, False, filteredimage is not None)
    else:
        gui.display_image(filteredimage)
        if filteredimage is not None:
            selection.selection_filtered()

def save():
    if selection.today:
        save_result(results[selection.timestamp])
    if selection.graph:
        save_graphimage(images_graph[selection.music])
    window['button_save'].update(disabled=True)

def filter():
    if selection.today:
        targetresult = results[selection.timestamp]

    if selection.timestamp in imagevalues_filtered.keys():
        gui.display_image(imagevalues_filtered[selection.timestamp], selection.today and not targetresult.saved)
    else:
        if selection.today:
            if targetresult.filtered is not None:
                filteredvalue = imagevalues_filtered[selection.timestamp]
            else:
                targetresult.filter()
                save_filtered(targetresult)
                filteredvalue = get_imagevalue(targetresult.filtered)
                imagevalues_filtered[selection.timestamp] = filteredvalue
            gui.display_image(filteredvalue, not targetresult.saved)
    
    selection.selection_filtered()

def open_folder():
    if selection.filtered:
        system(f'explorer.exe {filtereds_dirpath}')
        return
    
    if selection.graph:
        system(f'explorer.exe {graphs_dirpath}')
        return
    
    system(f'explorer.exe {results_dirpath}')

def tweet():
    if len(values['music_candidates']) == 1:
        music_text = tweet_template_music
        music_text = music_text.replace('&&play_mode&&', selection.play_mode)
        if selection.music is not None:
            music_text = music_text.replace('&&music&&', selection.music)
        else:
            music_text = music_text.replace('&&music&&', '?????')
        music_text = music_text.replace('&&D&&', selection.difficulty[0])
    else:
        if len(values['table_results']) > 0:
            musics_text = []
            for index in values['table_results']:
                text = tweet_template_music
                result = results[list_results[index][0]]
                music = result.informations.music
                music = music if music is not None else '?????'
                text = text.replace('&&play_mode&&', result.informations.play_mode)
                text = text.replace('&&music&&', music)
                text = text.replace('&&D&&', result.informations.difficulty[0])
                musics_text.append(text)
            music_text = '\n'.join(musics_text)
        else:
            music_text = ''

    text = quote('\n'.join((music_text, tweet_template_hashtag)))
    url = f'{tweet_url}?text={text}'
    webbrowser.open(url)

def delete_record():
    if selection is None:
        return

    if selection.music in records.keys():
        del records[selection.music]

    selection.record.delete()
    gui.search_music_candidates()

    gui.display_record(None)
    gui.display_image(None)

def delete_targetrecord():
    if selection is None:
        return
    if selection.timestamp is None:
        return

    selection.record.delete_history(
        selection.play_mode,
        selection.difficulty,
        selection.timestamp
    )

    gui.display_record(selection.get_targetrecord())
    gui.display_image(None)

def create_graph(selection, targetrecord):
    graphimage = create_graphimage(selection.play_mode, selection.difficulty, selection.music, targetrecord)
    if graphimage is None:
        return

    images_graph[selection.music] = graphimage

    imagevalue = get_imagevalue(graphimage)
    gui.display_image(imagevalue, True)
    
    selection.selection_graph()

if __name__ == '__main__':
    if setting.manage:
        keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = gui.generate_window(setting, version)

    display_screenshot_enable = False

    screenshot = None

    results = {}
    list_results = []
    records = {}
    imagevalues_result = {}
    imagevalues_filtered = {}
    images_graph = {}
    selection = None

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
            if event == 'text_file_path':
                if exists(values['text_file_path']):
                    screen = open_screenimage(values['text_file_path'])
                    gui.display_image(get_imagevalue(screen.original))
                    if recog.get_is_result(screen.monochrome):
                        result_process(screen)
            if event == 'button_save':
                save()
            if event == 'button_filter':
                filter()
            if event == 'button_tweet':
                tweet()
            if event == 'button_open_folder':
                open_folder()
            if event == 'table_results':
                selection_result = select_result_today()
                if selection_result is not None:
                    selection = selection_result
                    if selection.music is not None:
                        window['music_candidates'].update([selection.music], set_to_index=[0])
                    else:
                        window['music_candidates'].update(set_to_index=[])
            if event == 'button_graph':
                if selection is not None and selection.music is not None:
                    create_graph(selection, selection.get_targetrecord())
            if event == 'search_music':
                music_search_time = time.time() + 1
            if event in ['play_mode_sp', 'play_mode_dp', 'difficulty', 'music_candidates']:
                selection_result = select_music_search()
                if selection_result is not None:
                    selection = selection_result
            if event == '選択した曲の記録を削除する':
                delete_record()
                selection = None
            if event == 'history':
                select_timestamp()
            if event == '選択したリザルトの記録を削除する':
                delete_targetrecord()
            if event == 'timeout':
                if not window['positioned'].visible and thread.positioned:
                    window['positioned'].update(visible=True)
                if music_search_time is not None and time.time() > music_search_time:
                    music_search_time = None
                    gui.search_music_candidates()
                if not queue_log.empty():
                    log_debug(queue_log.get_nowait())
                if not queue_display_image.empty():
                    window['table_results'].update(select_rows=[])
                    window['music_candidates'].update(set_to_index=[])
                    selection = None
                    gui.display_image(get_imagevalue(queue_display_image.get_nowait()))
                if not queue_result_screen.empty():
                    result_process(queue_result_screen.get_nowait())
        except Exception as ex:
            log_debug(ex)
    
    window.close()
