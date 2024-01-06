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
from gui.setting import open_setting
from gui.export import open_export
from gui.general import get_imagevalue
from define import define
from resources import resource,play_sound_result,check_latest
from screenshot import Screenshot,open_screenimage
from recog import Recognition as recog
from raw_image import save_raw
from storage import StorageAccessor
from record import NotebookRecent,NotebookMusic,rename_allfiles,rename_changemusicname,musicnamechanges_filename
from graph import create_graphimage,save_graphimage
from result import result_save,result_savefiltered,get_resultimage,get_filteredimage
from filter import filter as filter_result
from playdata import Recent
from windows import find_window,get_rect,openfolder_results,openfolder_filtereds,openfolder_graphs

recent_maxcount = 100

thread_time_wait_nonactive = 1  # INFINITASがアクティブでないときのスレッド周期
thread_time_wait_loading = 30   # INFINITASがローディング中のときのスレッド周期
thread_time_normal = 0.3        # 通常のスレッド周期
thread_time_result = 0.12       # リザルトのときのスレッド周期

upload_confirm_message = [
    '曲名の誤認識を通報しますか？',
    'リザルトから曲名を切り取った画像をクラウドにアップロードします。'
]

windowtitle = 'beatmania IIDX INFINITAS'
exename = 'bm2dx.exe'

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'
tweet_url = 'https://twitter.com/intent/tweet'

tweet_template_music = '&&music&&[&&play_mode&&&&D&&]&&update&&&&option&&'
tweet_template_hashtag = '#IIDX #infinitas573 #infnotebook'

class ThreadMain(Thread):
    handle = 0
    active = False
    waiting = False
    confirmed_somescreen = False
    confirmed_processable = False
    processed = False
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
                self.confirmed_somescreen = False
                self.confirmed_processable = False
                self.processed = False
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
        
        if screen == 'music_select':
            if not shotted:
                screenshot.shot()
            version = recog.MusicSelect.get_version(screenshot.np_value)

        if not screen in ['result', 'music_select'] or (screen == 'music_select' and version is None):
            self.confirmed_somescreen = False
            self.confirmed_processable = False
            self.processed = False
            return
        
        if not self.confirmed_somescreen:
            self.confirmed_somescreen = True
            if screen == 'result':
                # リザルトのときのみ、スレッド周期を短くして取込タイミングを高速化する
                self.sleep_time = thread_time_result
        
        if self.processed:
            return
        
        if not shotted:
            screenshot.shot()
        
        if screen == 'result' and not recog.get_is_savable(screenshot.np_value):
            return
        
        if not self.confirmed_processable:
            self.confirmed_processable = True
            self.find_time = time.time()
            return

        if time.time() - self.find_time <= thread_time_normal*2-0.1:
            return

        if screen == 'result':
            resultscreen = screenshot.get_resultscreen()

            self.queues['result_screen'].put(resultscreen)

            self.sleep_time = thread_time_normal
            self.processed = True
        
        if screen == 'music_select':
            self.queues['musicselect_screen'].put(screenshot.np_value)

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
        if storage.upload_collection(result, resultimage, window['force_upload'].get()):
            timestamps_uploaded.append(result.timestamp)
    
    if setting.newrecord_only and not result.has_new_record():
        return
    
    if setting.play_sound:
        play_sound_result()
    
    images_result[result.timestamp] = resultimage

    saved = False
    if setting.autosave:
        save_result(result, resultimage)
        saved = True
    
    filtered = False
    if setting.autosave_filtered:
        save_filtered(
            resultimage,
            result.timestamp,
            result.informations.music,
            result.play_side,
            result.rival,
            result.details.graphtarget == 'rival'
        )
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

        notebook.insert(result)

    if not result.dead or result.has_new_record():
        recent.insert(result)

    insert_results(result)

def musicselect_process(np_value):
    playmode = recog.MusicSelect.get_playmode(np_value)
    if playmode is None:
        return
    
    difficulty = recog.MusicSelect.get_difficulty(np_value)
    if difficulty is None:
        return
    
    musicname = recog.MusicSelect.get_musicname(np_value)
    if musicname is None or not musicname in resource.musictable['musics'].keys():
        return
    
    music_information = resource.musictable['musics'][musicname]
    version = recog.MusicSelect.get_version(np_value)
    if version != music_information['version'] and (version in ['1st', 'substream'] and music_information['version'] != '1st&substream'):
        return

    if not playmode in music_information.keys():
        return
    if not difficulty in music_information[playmode].keys():
        return
    
    levels = recog.MusicSelect.get_levels(np_value)
    if not difficulty in levels.keys() or levels[difficulty] != music_information[playmode][difficulty]:
        return
    if musicname in notebooks_music.keys():
        notebook = notebooks_music[musicname]
    else:
        notebook = NotebookMusic(musicname) if musicname is not None else None
        notebooks_music[musicname] = notebook
    if notebook.update_best_musicselect({
        'playmode': playmode,
        'difficulty': difficulty,
        'cleartype': recog.MusicSelect.get_cleartype(np_value),
        'djlevel': recog.MusicSelect.get_djlevel(np_value),
        'score': recog.MusicSelect.get_score(np_value),
        'misscount': recog.MusicSelect.get_misscount(np_value),
        'levels': recog.MusicSelect.get_levels(np_value)
    }):
        notebook.save()
        if selection is not None and selection.play_mode == playmode and selection.music == musicname and selection.difficulty == difficulty:
            gui.display_record(selection.get_targetrecordlist())

def save_result(result, image):
    if result.timestamp in timestamps_saved:
        return
    
    ret = None
    try:
        music = result.informations.music
        ret = result_save(image, music, result.timestamp, setting.imagesave_path, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        timestamps_saved.append(result.timestamp)
        log_debug(f'save result: {ret}')

def save_filtered(resultimage, timestamp, music, play_side, loveletter, rivalname):
    """リザルト画像にぼかしを入れて保存する

    Args:
        image (Image): 対象の画像(PIL)
        timestamp (str): リザルトのタイムスタンプ
        music (str): 曲名
        play_side (str): 1P or 2P
        loveletter (bool): ライバル挑戦状の有無
        rivalname (bool): グラフターゲットのライバル名の有無

    Returns:
        Image: ぼかしを入れた画像
    """
    filteredimage = filter_result(resultimage, play_side, loveletter, rivalname)

    ret = None
    try:
        ret = result_savefiltered(filteredimage, music, timestamp, setting.imagesave_path, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        images_filtered[timestamp] = filteredimage
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
            '☑' if target['clear_type_new'] else '',
            '☑' if target['dj_level_new'] else '',
            '☑' if target['score_new'] else '',
            '☑' if target['miss_count_new'] else ''
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
    while len(list_results) > recent_maxcount:
        del list_results[-1]

    table_selected_rows = [v + 1 for v in table_selected_rows]
    refresh_table(setting.display_result)

def update_resultflag(row_index, saved=False, filtered=False):
    if saved:
        list_results[row_index][0] = '☑'
    if filtered:
        list_results[row_index][1] = '☑'

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
    informations_filename = f'{define.informations_resourcename}.res'
    if check_latest(storage, informations_filename):
        resource.load_resource_informations()

    details_filename = f'{define.details_resourcename}.res'
    if check_latest(storage, details_filename):
        resource.load_resource_details()

    musictable_filename = f'{define.musictable_resourcename}.res'
    if check_latest(storage, musictable_filename):
        resource.load_resource_musictable()
        gui.update_musictable()

    musicselect_filename = f'{define.musicselect_resourcename}.res'
    if check_latest(storage, musicselect_filename):
        resource.load_resource_musicselect()

    check_latest(storage, musicnamechanges_filename)
    rename_changemusicname()

    logger.info('complete check resources')

def select_result_recent():
    if len(table_selected_rows) == 0:
        return None

    window['music_candidates'].update(set_to_index=[])

    if len(table_selected_rows) != 1:
        return None
    
    timestamp = list_results[table_selected_rows[0]][2]
    target = notebook_recent.get_result(timestamp)

    if target['music'] is not None:
        if target['music'] in notebooks_music.keys():
            notebook = notebooks_music[target['music']]
        else:
            notebook = NotebookMusic(target['music'])
            notebooks_music[target['music']] = notebook
    else:
        notebook = None

    ret = Selection(
        target['play_mode'],
        target['difficulty'],
        target['music'],
        notebook
    )

    ret.selection_recent(timestamp)

    if timestamp in results_today.keys():
        display_today(ret)
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
        display_today(selection)
    else:
        display_history(selection)

def load_resultimages(timestamp, music, recent=False):
    image_result = get_resultimage(music, timestamp, setting.imagesave_path)
    images_result[timestamp] = image_result
    if image_result is not None:
        timestamps_saved.append(timestamp)

    image_filtered = get_filteredimage(music, timestamp, setting.imagesave_path)
    if not recent or image_result is None or image_filtered is not None:
        images_filtered[timestamp] = image_filtered

def display_today(selection):
    if selection.timestamp in imagevalues_result.keys():
        resultimage = imagevalues_result[selection.timestamp]
    else:
        resultimage = get_imagevalue(images_result[selection.timestamp])
        imagevalues_result[selection.timestamp] = resultimage
    gui.display_image(resultimage, result=True)

def display_history(selection):
    if not selection.timestamp in images_result.keys():
        load_resultimages(selection.timestamp, selection.music, selection.timestamp in notebook_recent.timestamps)
    
    if selection.timestamp in imagevalues_result.keys():
        imagevalue_result = imagevalues_result[selection.timestamp]
    else:
        imagevalue_result = get_imagevalue(images_result[selection.timestamp]) if selection.timestamp in images_result.keys() and images_result[selection.timestamp] is not None else None
        imagevalues_result[selection.timestamp] = imagevalue_result

    if imagevalue_result is not None:
        gui.display_image(imagevalue_result, result=True)
    else:
        if selection.timestamp in imagevalues_filtered.keys():
            imagevalue_filtered = imagevalues_filtered[selection.timestamp]
        else:
            imagevalue_filtered = get_imagevalue(images_filtered[selection.timestamp]) if selection.timestamp in images_filtered.keys() and images_filtered[selection.timestamp] is not None else None
            imagevalues_filtered[selection.timestamp] = imagevalue_filtered

        gui.display_image(imagevalue_filtered, result=True)
        if imagevalue_filtered is not None:
            selection.selection_filtered()

def save():
    if selection.recent:
        for row_index in table_selected_rows:
            timestamp = list_results[row_index][2]
            if timestamp in results_today.keys() and not timestamp in timestamps_saved:
                save_result(results_today[timestamp], images_result[timestamp])
                notebook_recent.get_result(timestamp)['saved'] = True
                update_resultflag(row_index, saved=True)
        notebook_recent.save()
        refresh_table()
    if selection.graph:
        save_graphimage(selection.music, images_graph[selection.music], setting.imagesave_path, setting.savefilemusicname_right)

def filter():
    """ライバル欄にぼかしを入れて、ぼかし画像を表示する

    最近のリザルトから選択している場合：
        選択しているすべてのリザルトにぼかし処理を実行する。
        ただし今日のリザルトでない場合は、リザルト画像がファイル保存されている場合のみ、処理が可能。

    曲検索から選択している場合：
        それが最近のリザルトに含まれている場合は、ぼかし処理ができない(tableのインデックスがわからないため)。
        ぼかし画像の有無の確認のみ行い、画像がある場合はそれを表示する。
    """
    if selection.recent:
        updated = False
        for row_index in table_selected_rows:
            timestamp = list_results[row_index][2]
            target = notebook_recent.get_result(timestamp)
            if not timestamp in images_result.keys():
                load_resultimages(timestamp, target['music'], True)
            if images_result[timestamp] is not None and not timestamp in images_filtered.keys():
                save_filtered(
                    images_result[timestamp],
                    timestamp,
                    target['music'],
                    target['play_side'],
                    target['has_loveletter'],
                    target['has_graphtargetname']
                )
                target['filtered'] = True
                update_resultflag(row_index, filtered=True)
                updated = True
        if updated:
            notebook_recent.save()
            refresh_table()
    else:
        if not selection.timestamp in images_result.keys() and not selection.timestamp in notebook_recent.timestamps:
            load_resultimages(selection.timestamp, selection.music)

    if selection.timestamp in imagevalues_filtered.keys():
        imagevalue = imagevalues_filtered[selection.timestamp]
    else:
        filteredimage = images_filtered[selection.timestamp] if selection.timestamp in images_filtered.keys() else None
        imagevalue = get_imagevalue(filteredimage) if filteredimage is not None else None
        if imagevalue is not None:
            imagevalues_filtered[selection.timestamp] = imagevalue

    if imagevalue is not None:
        gui.display_image(imagevalue, result=True)
        selection.selection_filtered()

def upload():
    if not selection.recent:
        return
    
    if not gui.question('確認', upload_confirm_message):
        return
    
    for row_index in table_selected_rows:
        timestamp = list_results[row_index][2]
        if timestamp in results_today.keys() and not timestamp in timestamps_uploaded:
            storage.upload_collection(results_today[timestamp], images_result[timestamp], True)
            timestamps_uploaded.append(timestamp)

def open_folder_results():
    ret = openfolder_results(setting.imagesave_path)
    if ret is not None:
        logger.exception(ret)
        gui.error_message(u'失敗', u'フォルダを開くのに失敗しました。', ret)

def open_folder_filtereds():
    ret = openfolder_filtereds(setting.imagesave_path)
    if ret is not None:
        logger.exception(ret)
        gui.error_message(u'失敗', u'フォルダを開くのに失敗しました。', ret)
    
def open_folder_graphs():
    ret = openfolder_graphs(setting.imagesave_path)
    if ret is not None:
        logger.exception(ret)
        gui.error_message(u'失敗', u'フォルダを開くのに失敗しました。', ret)

def tweet():
    if len(values['table_results']) > 0:
        musics_text = []
        for index in reversed(values['table_results']):
            result = notebook_recent.get_result(list_results[index][2])

            music = result['music']
            music = music if music is not None else '??????'

            text = tweet_template_music
            text = text.replace('&&play_mode&&', result['play_mode'])
            text = text.replace('&&D&&', result['difficulty'][0])
            text = text.replace('&&music&&', music)
            if result['update_clear_type'] is not None or result['update_dj_level'] is not None:
                text = text.replace('&&update&&', ' '.join(v for v in [result['update_clear_type'], result['update_dj_level']] if v is not None))
            else:
                if result['update_score'] is not None:
                    text = text.replace('&&update&&', f"自己ベスト+{result['update_score']}")
                else:
                    if result['update_miss_count'] is not None:
                        text = text.replace('&&update&&', f"ミスカウント{result['update_miss_count']}")
                    else:
                        text = text.replace('&&update&&', '')
            if not selection.graph and result['option'] is not None:
                if result['option'] == '':
                    text = text.replace('&&option&&', '(正規)')
                else:
                    text = text.replace('&&option&&', f"({result['option']})")
            else:
                text = text.replace('&&option&&', '')

            musics_text.append(text)
        music_text = '\n'.join(musics_text)
    else:
        if len(values['music_candidates']) == 1:
            music_text = tweet_template_music
            music_text = music_text.replace('&&play_mode&&', selection.play_mode)
            if selection.music is not None:
                music_text = music_text.replace('&&music&&', selection.music)
            else:
                music_text = music_text.replace('&&music&&', '?????')
            music_text = music_text.replace('&&D&&', selection.difficulty[0])
            music_text = music_text.replace('&&update&&', '')
            music_text = music_text.replace('&&option&&', '')
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
    gui.display_image(imagevalue, graph=True)
    
    selection.selection_graph()

if __name__ == '__main__':
    keyboard.add_hotkey('alt+F10', active_screenshot)

    window = gui.generate_window(setting, version)

    display_screenshot_enable = False

    screenshot = Screenshot()

    notebook_recent = NotebookRecent(recent_maxcount)
    notebooks_music = {}

    results_today = {}
    timestamps_saved = []
    timestamps_uploaded = []

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
    queue_musicselect_screen = Queue()

    storage = StorageAccessor()

    event_close = Event()
    thread = ThreadMain(
        event_close,
        queues = {
            'log': queue_log,
            'display_image': queue_display_image,
            'result_screen': queue_result_screen,
            'musicselect_screen': queue_musicselect_screen
        }
    )

    music_search_time = None

    if not setting.has_key('data_collection'):
        setting.data_collection = gui.collection_request('resources/annotation.png')
        setting.save()
        if setting.data_collection:
            window['button_upload'].update(visible=True)

    if version != '0.0.0.0' and get_latest_version() != version:
        gui.find_latest_version(latest_url)

    if not setting.ignore_download:
        Thread(target=check_resource).start()
    
    if resource.musictable is not None:
        rename_allfiles(resource.musictable['musics'].keys())

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
            if event == 'text_file_path':
                if exists(values['text_file_path']):
                    screen = open_screenimage(values['text_file_path'])
                    gui.display_image(get_imagevalue(screen.original))
                    if recog.get_is_savable(screen.np_value):
                        result_process(screen)
            if event == 'button_setting':
                open_setting(setting)
                window['button_upload'].update(visible=setting.data_collection)
            if event == 'button_save':
                save()
            if event == 'button_filter':
                filter()
            if event == 'button_open_folder_results':
                open_folder_results()
            if event == 'button_open_folder_filtereds':
                open_folder_filtereds()
            if event == 'button_open_folder_graphs':
                open_folder_graphs()
            if event == 'button_tweet':
                tweet()
            if event == 'button_export':
                open_export(recent)
            if event == 'button_upload':
                upload()
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
            if event == 'category_versions':
                gui.search_music_candidates()
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
                if not queue_musicselect_screen.empty():
                    musicselect_process(queue_musicselect_screen.get_nowait())
        except Exception as ex:
            log_debug(ex)
    
    window.close()

    del screenshot
