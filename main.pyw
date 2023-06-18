import keyboard
import time
import PySimpleGUI as sg
from threading import Thread,Event
from queue import Queue
from os.path import join,exists,pardir
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
from gui.export import open_export
from gui.general import get_imagevalue
from define import define
from resources import play_sound_result,check_latest
from screenshot import Screenshot,open_screenimage
from recog import recog
from raw_image import save_raw
from storage import StorageAccessor
from record import NotebookRecent,NotebookMusic,rename_allfiles
from graph import create_graphimage,save_graphimage
from result import result_save,result_savefiltered,get_resultimagevalue,get_filteredimagevalue
from filter import filter as filter_result
from playdata import Recent
from windows import find_window,get_rect,openfolder_results,openfolder_filtereds,openfolder_graphs

thread_time_wait_nonactive = 1
thread_time_wait_loading = 30
thread_time_normal = 0.3
thread_time_result = 0.12

upload_confirm_message = [
    '曲名の誤認識を通報しますか？',
    'リザルトから曲名を切り取った画像をクラウドにアップロードします。'
]

windowtitle = 'beatmania IIDX INFINITAS'
exename = 'bm2dx.exe'

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'
tweet_url = 'https://twitter.com/intent/tweet'

tweet_template_music = '&&music&&[&&play_mode&&&&D&&]'
tweet_template_hashtag = '#IIDX #infinitas573 #infnotebook'

class ThreadMain(Thread):
    handle = 0
    active = False
    waiting = False
    confirmed_result = False
    confirmed_savable = False
    processed_result = False
    screen_latest = None

    def __init__(self, event_close, queues):
        self.event_close = event_close
        self.queues = queues

        Thread.__init__(self)

        self.start()

    def run(self):
        self.sleep_time = thread_time_wait_nonactive
        self.queues['log'].put('start thread')
        while not self.event_close.wait(timeout=self.sleep_time):
            self.routine()

    def routine(self):
        if self.handle == 0:
            self.handle = find_window(windowtitle, exename)
            if self.handle == 0:
                return

            self.queues['log'].put(f'infinitas find')
            self.active = False
            screenshot.xy = None
        
        rect = get_rect(self.handle)
        width = rect.right - rect.left
        height = rect.bottom - rect.top

        if rect is None or not width or not height:
            self.queues['log'].put(f'infinitas lost')
            self.sleep_time = thread_time_wait_nonactive

            self.handle = 0
            self.active = False
            screenshot.xy = None
            return
            
        if width != define.width or height != define.height:
            if self.active:
                self.queues['log'].put(f'infinitas deactivate')
                self.sleep_time = thread_time_wait_nonactive

            self.active = False
            screenshot.xy = None
            return
        
        if not self.active:
            self.active = True
            self.waiting = False
            self.queues['log'].put(f'infinitas activate')
            self.sleep_time = thread_time_normal
            screenshot.xy = (rect.left, rect.top)

        screen = screenshot.get_screen()

        if screen != self.screen_latest:
            self.screen_latest = screen

        if screen == 'loading':
            if not self.waiting:
                self.confirmed_result = False
                self.confirmed_savable = False
                self.processed_result = False
                self.waiting = True
                self.queues['log'].put('find loading: start waiting')
                self.sleep_time = thread_time_wait_loading
            return
            
        if self.waiting:
            self.waiting = False
            self.queues['log'].put('lost loading: end waiting')
            self.sleep_time = thread_time_normal

        shotted = False
        if display_screenshot_enable:
            screenshot.shot()
            shotted = True
            self.queues['display_image'].put(screenshot.get_image())
        
        if screen != 'result':
            self.confirmed_result = False
            self.confirmed_savable = False
            self.processed_result = False
            return
        
        if not self.confirmed_result:
            self.confirmed_result = True
            self.sleep_time = thread_time_result
        
        if self.processed_result:
            return
        
        if not shotted:
            screenshot.shot()
        
        if not recog.get_is_savable(screenshot.np_value):
            return
        
        if not self.confirmed_savable:
            self.confirmed_savable = True
            self.find_time = time.time()
            return

        if time.time() - self.find_time <= thread_time_normal*2-0.1:
            return

        resultscreen = screenshot.get_resultscreen()

        self.processed = True
        self.queues['result_screen'].put(resultscreen)
        if setting.play_sound:
            play_sound_result()

        self.sleep_time = thread_time_normal
        self.processed_result = True

class Selection():
    def __init__(self, play_mode, difficulty, music, notebook):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.music = music
        self.notebook = notebook
        self.recent = False
        self.filtered = False
        self.graph = False
        self.timestamp = None
    
    def selection_recent(self, timestamp):
        self.recent = True
        self.filtered = False
        self.graph = False
        self.timestamp = timestamp

    def selection_graph(self):
        if self.music is None:
            return False
        
        self.recent = False
        self.filtered = False
        self.graph = True
        self.timestamp = None

        return True

    def selection_timestamp(self, timestamp):
        self.recent = False
        self.filtered = False
        self.graph = False
        self.timestamp = timestamp
    
    def selection_filtered(self):
        self.filtered = True
        self.graph = False

    def get_targetrecordlist(self):
        return self.notebook.get_recordlist(self.play_mode, self.difficulty)

def result_process(screen):
    """リザルトを記録するときの処理をする

    Args:
        screen (Screen): screen.py
    """
    result = recog.get_result(screen)
    if result is None:
        return

    resultimage = screen.original
    if setting.data_collection or window['force_upload'].get():
        newrecog_result = recog.check_newrecognition(result, screen.np_value)
        storage.upload_collection(result, window['force_upload'].get() or not newrecog_result)
    
    if setting.newrecord_only and not result.has_new_record():
        return
    
    images_result[result.timestamp] = resultimage

    saved = False
    if setting.autosave:
        save_result(result, resultimage)
        saved = True
    
    filtered = False
    if setting.autosave_filtered:
        save_filtered(result, resultimage)
        filtered = True
    
    notebook_recent.append(result, saved, filtered)
    notebook_recent.save()

    music = result.informations.music
    if music is not None:
        if music in notebooks_music.keys():
            notebook = notebooks_music[music]
        else:
            notebook = NotebookMusic(music) if music is not None else None
            notebooks_music[music] = notebook

        if not result.dead or result.has_new_record():
            notebook.insert(result)
            notebook.save()

    if not result.dead or result.has_new_record():
        recent.insert(result)

    insert_results(result)

def save_result(result, image):
    if result.timestamp in timestamps_saved:
        return
    
    ret = None
    try:
        music = result.informations.music
        ret = result_save(image, music, result.timestamp, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        timestamps_saved.append(result.timestamp)
        log_debug(f'save result: {ret}')

def save_filtered(result, resultimage):
    if result.timestamp in images_filtered.keys():
        return
    
    filteredimage = filter_result(result, resultimage)

    ret = None
    try:
        music = result.informations.music
        ret = result_savefiltered(filteredimage, music, result.timestamp, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        images_filtered[result.timestamp] = filteredimage
        log_debug(f'save filtered result: {ret}')

def insert_recentnotebook_results():
    for timestamp in notebook_recent.timestamps:
        target = notebook_recent.get_result(timestamp)
        playmode = target['play_mode']
        difficulty = target['difficulty']
        list_results.insert(0, [
            '☑' if target['saved'] else '',
            '☑' if target['filtered'] else '',
            timestamp,
            target['music'] if target['music'] is not None else '??????',
            f'{playmode}{difficulty[0]}' if playmode is not None and difficulty is not None else '???',
            '☑' if target['clear_type'] else '',
            '☑' if target['dj_level'] else '',
            '☑' if target['score'] else '',
            '☑' if target['miss_count'] else ''
        ])

    refresh_table()

def insert_results(result):
    global table_selected_rows

    results_today[result.timestamp] = result

    play_mode = result.informations.play_mode
    difficulty = result.informations.difficulty
    music = result.informations.music

    list_results.insert(0, [
        '☑' if result.timestamp in timestamps_saved else '',
        '☑' if result.timestamp in images_filtered.keys() else '',
        result.timestamp,
        music if music is not None else '??????',
        f'{play_mode}{difficulty[0]}' if play_mode is not None and difficulty is not None else '???',
        '☑' if result.details.clear_type.new else '',
        '☑' if result.details.dj_level.new else '',
        '☑' if result.details.score.new else '',
        '☑' if result.details.miss_count.new else ''
    ])

    table_selected_rows = [v + 1 for v in table_selected_rows]
    refresh_table(setting.display_result)

def update_resultflag(saved=False, filtered=False):
    for row_index in table_selected_rows:
        if saved:
            list_results[row_index][0] = '☑'
        if filtered:
            list_results[row_index][1] = '☑'
    refresh_table()

def refresh_table(select_newest=False):
    if select_newest:
        window['table_results'].update(values=list_results, select_rows=[0])
    else:
        window['table_results'].update(values=list_results, select_rows=table_selected_rows)

def clear_tableselection():
    table_selected_rows = []
    window['table_results'].update(select_rows=table_selected_rows)

def active_screenshot():
    if not screenshot.shot():
        return
    
    image = screenshot.get_image()
    if image is not None:
        filepath = save_raw(image)
        log_debug(f'save screen: {filepath}')
        gui.display_image(get_imagevalue(image))
        window['screenshot_filepath'].update(join(pardir, filepath))

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

def check_resource():
    musics_filename = f'{define.musics_resourcename}.json'
    if check_latest(storage, musics_filename):
        recog.load_resource_musics()

    informations_filename = f'{define.informations_resourcename}.res'
    if check_latest(storage, informations_filename):
        recog.load_resource_informations()

def select_result_recent():
    if len(table_selected_rows) == 0:
        return None

    window['music_candidates'].update(set_to_index=[])

    if len(table_selected_rows) != 1:
        return None
    
    timestamp = list_results[table_selected_rows[0]][2]
    target = notebook_recent.get_result(timestamp)

    if target['music'] in notebooks_music.keys():
        notebook = notebooks_music[target['music']]
    else:
        notebook = NotebookMusic(target['music'])
        notebooks_music[target['music']] = notebook

    ret = Selection(
        target['play_mode'],
        target['difficulty'],
        target['music'],
        notebook
    )

    ret.selection_recent(timestamp)

    if timestamp in results_today.keys():
        display_today(timestamp)
    else:
        display_history(ret)
    
    if ret.notebook is not None:
        if ret.play_mode == 'SP':
            window['play_mode_sp'].update(True)
        if ret.play_mode == 'DP':
            window['play_mode_dp'].update(True)
        
        window['difficulty'].update(ret.difficulty)
        window['search_music'].update(target['music'])

        targetrecordlist = ret.get_targetrecordlist()
        gui.display_record(targetrecordlist)
        gui.display_historyresult(targetrecordlist, timestamp)
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

    clear_tableselection()

    if music in notebooks_music.keys():
        notebook = notebooks_music[music]
    else:
        notebook = NotebookMusic(music)
        notebooks_music[music] = notebook

    targetrecordlist = notebook.get_recordlist(play_mode, difficulty)
    if targetrecordlist is None:
        gui.display_record(None)
        gui.display_image(None)
        return None

    ret = Selection(play_mode, difficulty, music, notebook)

    gui.display_record(targetrecordlist)
    create_graph(ret, targetrecordlist)

    return ret

def select_history():
    if len(values['history']) != 1:
        return
    
    clear_tableselection()

    timestamp = values['history'][0]
    selection.selection_timestamp(timestamp)

    gui.display_historyresult(selection.get_targetrecordlist(), timestamp)

    if timestamp in results_today.keys():
        display_today(timestamp)
    else:
        display_history(selection)

def load_resultimagevalues(timestamp, music):
    imagevalues_result[timestamp] = get_resultimagevalue(music, timestamp)
    imagevalues_filtered[timestamp] = get_filteredimagevalue(music, timestamp)

def display_today(timestamp):
    if timestamp in imagevalues_result.keys():
        resultimage = imagevalues_result[timestamp]
    else:
        resultimage = get_imagevalue(images_result[timestamp])
        imagevalues_result[timestamp] = resultimage
    gui.display_image(resultimage, not timestamp in timestamps_saved, True, True)

def display_history(selection):
    if not selection.timestamp in imagevalues_result.keys():
        load_resultimagevalues(selection.timestamp, selection.music)
    
    imagevalue_result =  imagevalues_result[selection.timestamp]
    imagevalue_filtered =  imagevalues_filtered[selection.timestamp]
    if imagevalue_result is not None:
        gui.display_image(imagevalue_result, False, imagevalue_filtered is not None, False)
    else:
        if imagevalue_filtered is not None:
            gui.display_image(imagevalue_filtered, False, False, False)
            selection.selection_filtered()
        else:
            gui.display_image(None)

def save():
    if selection.recent:
        for row_index in table_selected_rows:
            timestamp = list_results[row_index][2]
            save_result(results_today[timestamp], images_result[timestamp])
            notebook_recent.get_result(timestamp)['saved'] = True
            notebook_recent.save()
        update_resultflag(saved=True)
    if selection.graph:
        save_graphimage(selection.music, images_graph[selection.music], setting.savefilemusicname_right)
    window['button_save'].update(disabled=True)

def filter():
    if selection.recent and selection.timestamp in results_today.keys():
        for row_index in table_selected_rows:
            timestamp = list_results[row_index][2]
            targetresult = results_today[timestamp]
            if not timestamp in images_filtered.keys():
                save_filtered(targetresult, images_result[timestamp])
                notebook_recent.get_result(timestamp)['filtered'] = True
                notebook_recent.save()
            update_resultflag(filtered=True)

    if selection.timestamp in imagevalues_filtered.keys():
        imagevalue = imagevalues_filtered[selection.timestamp]
    else:
        filteredimage = images_filtered[selection.timestamp]
        imagevalue = get_imagevalue(filteredimage)
        imagevalues_filtered[selection.timestamp] = imagevalue

    gui.display_image(
        imagevalue,
        selection.recent and not selection.timestamp in timestamps_saved
    )
    
    selection.selection_filtered()

def open_folder():
    if selection.filtered:
        openfolder_filtereds()
        return
    
    if selection.graph:
        openfolder_graphs()
        return
    
    openfolder_results()

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
                result = results_today[list_results[index][2]]
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

    if selection.music in notebooks_music.keys():
        del notebooks_music[selection.music]

    selection.notebook.delete()
    gui.search_music_candidates()

    gui.display_record(None)
    gui.display_image(None)

def delete_targetrecord():
    if selection is None:
        return
    if selection.timestamp is None:
        return

    selection.notebook.delete_history(
        selection.play_mode,
        selection.difficulty,
        selection.timestamp
    )

    gui.display_record(selection.get_targetrecordlist())
    gui.display_image(None)

def create_graph(selection, targetrecord):
    graphimage = create_graphimage(selection.play_mode, selection.difficulty, selection.music, targetrecord)
    if graphimage is None:
        return

    images_graph[selection.music] = graphimage

    imagevalue = get_imagevalue(graphimage)
    gui.display_image(imagevalue, True)
    
    selection.selection_graph()

def rename_all_musicnotebooks():
    if recog.musics is None:
        return

    def covering(target, musics):
        if type(target) is dict:
            for t in target.values():
                covering(t, musics)
        else:
            musics.append(target)

    musics = []
    covering(recog.music_recognition, musics)
    musics = set(musics)

    rename_allfiles(musics)

if __name__ == '__main__':
    keyboard.add_hotkey('ctrl+F10', active_screenshot)

    window = gui.generate_window(setting, version)

    display_screenshot_enable = False

    screenshot = Screenshot()

    notebook_recent = NotebookRecent()
    notebooks_music = {}

    results_today = {}
    timestamps_saved = []

    images_result = {}
    images_filtered = {}
    imagevalues_result = {}
    imagevalues_filtered = {}

    images_graph = {}

    selection = None

    recent = Recent()

    list_results = []
    table_selected_rows = []

    queue_log = Queue()
    queue_display_image = Queue()
    queue_result_screen = Queue()

    storage = StorageAccessor()

    event_close = Event()
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
        if setting.data_collection:
            window['button_upload'].update(visible=True)

    if version != '0.0.0.0' and get_latest_version() != version:
        gui.find_latest_version(latest_url)

    if not setting.ignore_download:
        Thread(target=check_resource).start()
    
    # version0.7.0.1以前の不具合対応のため
    rename_all_musicnotebooks()

    insert_recentnotebook_results()

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
            if event == 'check_savefilemusicname_right':
                setting.savefilemusicname_right = values['check_savefilemusicname_right']
            if event == 'text_file_path':
                if exists(values['text_file_path']):
                    screen = open_screenimage(values['text_file_path'])
                    gui.display_image(get_imagevalue(screen.original))
                    if recog.get_is_savable(screen.np_value):
                        result_process(screen)
            if event == 'button_save':
                save()
            if event == 'button_filter':
                filter()
            if event == 'button_open_folder':
                open_folder()
            if event == 'button_tweet':
                tweet()
            if event == 'button_export':
                open_export(recent)
            if event == 'button_upload':
                if gui.question('確認', upload_confirm_message):
                    result = results_today[selection.timestamp]
                    storage.upload_collection(result, True)
            if event == 'table_results':
                if values['table_results'] != table_selected_rows:
                    table_selected_rows = values['table_results']
                    selection_result = select_result_recent()
                    if selection_result is not None:
                        selection = selection_result
                        if selection.music is not None:
                            window['music_candidates'].update([selection.music], set_to_index=[0])
                        else:
                            window['music_candidates'].update(set_to_index=[])
            if event == 'button_graph':
                if selection is not None and selection.music is not None:
                    create_graph(selection, selection.get_targetrecordlist())
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
                select_history()
            if event == '選択したリザルトの記録を削除する':
                delete_targetrecord()
            if event == 'button_best_switch':
                gui.switch_best_display()
            if event == 'timeout':
                if not window['positioned'].visible and thread.handle:
                    window['positioned'].update(visible=True)
                if window['positioned'].visible and not thread.handle:
                    window['positioned'].update(visible=False)
                if not window['captureenable'].visible and screenshot.xy:
                    window['captureenable'].update(visible=True)
                if window['captureenable'].visible and not screenshot.xy:
                    window['captureenable'].update(visible=False)
                if music_search_time is not None and time.time() > music_search_time:
                    music_search_time = None
                    gui.search_music_candidates()
                if not queue_log.empty():
                    log_debug(queue_log.get_nowait())
                if not queue_display_image.empty():
                    clear_tableselection()
                    window['music_candidates'].update(set_to_index=[])
                    selection = None
                    gui.display_image(get_imagevalue(queue_display_image.get_nowait()))
                if not queue_result_screen.empty():
                    result_process(queue_result_screen.get_nowait())
        except Exception as ex:
            log_debug(ex)
    
    window.close()

    del screenshot
