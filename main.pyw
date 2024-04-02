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
from PIL import Image

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
from gui.general import get_imagevalue,progress,question
from define import define
from resources import resource,play_sound_result,check_latest,images_resourcecheck_filepath
from screenshot import Screenshot,open_screenimage
from recog import Recognition as recog
from raw_image import save_raw
from storage import StorageAccessor
from record import NotebookRecent,NotebookSummary,NotebookMusic,rename_allfiles,rename_changemusicname,musicnamechanges_filename
from graph import create_graphimage
from filter import filter as filter_result
from export import Recent,output
from windows import find_window,get_rect,openfolder_results,openfolder_filtereds,openfolder_graphs,openfolder_scoreinformations
from image import save_resultimage,save_resultimage_filtered,save_scoreinformationimage,save_graphimage,get_resultimage,get_resultimage_filtered,generateimage_summary,generateimage_musicinformation

recent_maxcount = 100

thread_time_wait_nonactive = 1  # INFINITASがアクティブでないときのスレッド周期
thread_time_wait_loading = 30   # INFINITASがローディング中のときのスレッド周期
thread_time_normal = 0.3        # 通常のスレッド周期
thread_time_result = 0.12       # リザルトのときのスレッド周期
thread_time_musicselect = 0.1   # 選曲のときのスレッド周期

upload_confirm_message = [
    '曲名の誤認識を通報しますか？',
    'リザルトから曲名を切り取った画像をクラウドにアップロードします。'
]

windowtitle = 'beatmania IIDX INFINITAS'
exename = 'bm2dx.exe'
notebooksummary_confirm_message = [
    '各曲の記録ファイルから１つのまとめ記録ファイルを作成しています。',
    '時間がかかる場合がありますが次回からは実行されません。'
]

latest_url = 'https://github.com/kaktuswald/inf-notebook/releases/latest'
tweet_url = 'https://twitter.com/intent/tweet'

tweet_template_music = '&&music&&[&&play_mode&&&&D&&]&&update&&&&option&&'
tweet_template_hashtag = '#IIDX #infinitas573 #infnotebook'

musicselect_targetrecord = None

image_summary = None

waitloading_title = 'インフィニタス ローディング'
waitloading_message = '\n'.join([
    "しばらくお待ちください。",
    "30秒ごとにローディングの状況をチェックします。"
])

class ThreadMain(Thread):
    handle = 0
    active = False
    waiting = False
    musicselect = False
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
            self.queues['messages'].put('hotkey_stop')

            return
            
        if width != define.width or height != define.height:
            if self.active:
                self.sleep_time = thread_time_wait_nonactive
                self.queues['log'].put(f'infinitas deactivate: {self.sleep_time}')
                self.queues['messages'].put('hotkey_stop')

            self.active = False
            screenshot.xy = None
            return
        
        if not self.active:
            self.active = True
            self.waiting = False
            self.musicselect = False
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'infinitas activate: {self.sleep_time}')
            self.queues['messages'].put('hotkey_start')
        
        screenshot.xy = (rect.left, rect.top)
        screen = screenshot.get_screen()

        if screen != self.screen_latest:
            self.confirmed_somescreen = False
            self.confirmed_processable = False
            self.processed = False
            self.screen_latest = screen

        if screen == 'loading':
            if not self.waiting:
                self.waiting = True
                self.musicselect = False
                self.sleep_time = thread_time_wait_loading
                self.queues['log'].put(f'find loading: start waiting: {self.sleep_time}')
                self.queues['messages'].put('detect_loading')
            return
            
        if self.waiting:
            self.waiting = False
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'lost loading: end waiting: {self.sleep_time}')

        # ここから先はローディング中じゃないときのみ
        
        shotted = False
        if display_screenshot_enable:
            screenshot.shot()
            shotted = True
            self.queues['display_image'].put(screenshot.get_image())
        
        if screen != 'music_select' and self.musicselect:
            # 画面が選曲から抜けたとき
            self.musicselect = False
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'screen out music select: {self.sleep_time}')

        if screen == 'music_select':
            if not self.musicselect:
                # 画面が選曲に入ったとき
                self.musicselect = True
                self.sleep_time = thread_time_musicselect
                self.queues['log'].put(f'screen in music select: {self.sleep_time}')

            if not shotted:
                screenshot.shot()
            trimmed = screenshot.np_value[define.musicselect_trimarea_np]
            if recog.MusicSelect.get_version(trimmed) is not None:
                self.queues['musicselect_screen'].put(trimmed)
            return

        if screen != 'result':
            self.confirmed_somescreen = False
            self.confirmed_processable = False
            self.processed = False
            return
        
        # ここから先はリザルトのみ

        if not self.confirmed_somescreen:
            self.confirmed_somescreen = True
            if screen == 'result':
                # リザルトのときのみ、スレッド周期を短くして取込タイミングを高速化する
                self.sleep_time = thread_time_result
                self.queues['log'].put(f'screen in result: {self.sleep_time}')
        
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
            self.queues['log'].put(f'processing result screen: {self.sleep_time}')
            self.processed = True

class Selection():
    def __init__(self, play_mode, difficulty, music, notebook):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.music = music
        self.notebook = notebook
        self.recent = False
        self.filtered = False
        self.scoreinformation = False
        self.graph = False
        self.timestamp = None
        self.image = None
    
    def selection_recent(self, timestamp):
        self.recent = True
        self.filtered = False
        self.scoreinformation = False
        self.graph = False
        self.timestamp = timestamp
        self.image = None

    def selection_scoreinformation(self, image):
        if self.music is None:
            return False
        
        self.recent = False
        self.filtered = False
        self.scoreinformation = True
        self.graph = False
        self.timestamp = None
        self.image = image

        return True

    def selection_graph(self, image):
        if self.music is None:
            return False
        
        self.recent = False
        self.filtered = False
        self.scoreinformation = False
        self.graph = True
        self.timestamp = None
        self.image = image

        return True

    def selection_timestamp(self, timestamp):
        self.recent = False
        self.filtered = False
        self.scoreinformation = False
        self.graph = False
        self.timestamp = timestamp
        self.image = None
    
    def selection_filtered(self):
        self.filtered = True
        self.scoreinformation = False
        self.graph = False
        self.image = None

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
        if storage.start_uploadcollection(result, resultimage, window['force_upload'].get()):
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
            result.informations.play_mode,
            result.informations.difficulty,
            result.play_side,
            result.rival,
            result.details.graphtarget == 'rival'
        )
        filtered = True
    
    notebook_recent.append(result, saved, filtered)
    notebook_recent.save()

    music = result.informations.music
    if music is not None:
        notebook = get_notebook_targetmusic(music)

        notebook.insert(result)
        notebook_summary.import_targetmusic(music, notebook)
        notebook_summary.save()
        summaryimage_generate()

    if not result.dead or result.has_new_record():
        recent.insert(result)

    insert_results(result)

def musicselect_process(np_value):
    global musicselect_targetrecord

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
    
    notebook = get_notebook_targetmusic(musicname)
    
    targetrecord = notebook.get_recordlist(playmode, difficulty)
    if targetrecord is not None and targetrecord is musicselect_targetrecord:
        return

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
        notebook_summary.import_targetmusic(musicname, notebook)
        notebook_summary.save()
        summaryimage_generate()
    
    musicselect_targetrecord = notebook.get_recordlist(playmode, difficulty)

    clear_tableselection()
    gui.display_record(musicselect_targetrecord)
    window['music_candidates'].update([musicname], set_to_index=[0])
    gui.display_historyresult(musicselect_targetrecord, None)
    image = generateimage_musicinformation(playmode, difficulty, musicname, musicselect_targetrecord)
    gui.display_image(get_imagevalue(image))

def save_result(result, image):
    if result.timestamp in timestamps_saved:
        return
    
    ret = None
    try:
        music = result.informations.music
        scoretype = {'playmode': result.informations.play_mode, 'difficulty': result.informations.difficulty}
        ret = save_resultimage(image, music, result.timestamp, setting.imagesave_path, scoretype, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        timestamps_saved.append(result.timestamp)

def save_filtered(resultimage, timestamp, music, play_mode, difficulty, play_side, loveletter, rivalname):
    """リザルト画像にぼかしを入れて保存する

    Args:
        image (Image): 対象の画像(PIL)
        timestamp (str): リザルトのタイムスタンプ
        music (str): 曲名
        play_mode (str): プレイモード
        difficulty (str): 譜面難易度
        play_side (str): 1P or 2P
        loveletter (bool): ライバル挑戦状の有無
        rivalname (bool): グラフターゲットのライバル名の有無

    Returns:
        Image: ぼかしを入れた画像
    """
    filteredimage = filter_result(resultimage, play_side, loveletter, rivalname, setting.filter_compact)

    ret = None
    try:
        scoretype = {'playmode': play_mode, 'difficulty': difficulty}
        ret = save_resultimage_filtered(filteredimage, music, timestamp, setting.imagesave_path, scoretype, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        gui.error_message(u'保存の失敗', u'リザルトの保存に失敗しました。', ex)
        return

    if ret:
        images_filtered[timestamp] = filteredimage

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

def upload_musicselect():
    """
    選曲画面の一部を学習用にアップロードする
    """
    if not screenshot.shot():
        return
    
    image = screenshot.get_image()
    if image is not None:
        storage.start_uploadmusicselect(image)
        log_debug(f'upload screen')
        gui.display_image(get_imagevalue(image))

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

    logger.info('complete check resources')

    changed = rename_changemusicname()
    queue_functions.put((notebooksummary_startimport, changed))

def notebooksummary_startimport(changed):
    """全曲記録データを各曲記録ファイルから作成する

    Note:
        バージョン0.14.2.1以前からjson構造変更
        バージョン0.15.2.0以降の初回起動で必ず実行する
    """

    if not 'last_allimported' in notebook_summary.json.keys():
        notebook_summary.json = {}
        counter = notebook_summary.start_import()
        progress("お待ちください", notebooksummary_confirm_message, counter, window.current_location())

        notebook_summary.json['last_allimported'] = version
        notebook_summary.save()
    else:
        for musicname, renamed in changed:
            del notebook_summary.json['musics'][musicname]
            notebook = get_notebook_targetmusic(renamed)
            notebook_summary.import_targetmusic(renamed, notebook)

        if len(changed) > 0:
            notebook_summary.save()
    
    summaryimage_generate()
    summaryimage_display()

def select_result_recent():
    if len(table_selected_rows) == 0:
        return None

    window['music_candidates'].update(set_to_index=[])

    if len(table_selected_rows) != 1:
        return None
    
    timestamp = list_results[table_selected_rows[0]][2]
    target = notebook_recent.get_result(timestamp)

    if target['music'] is not None:
        notebook = get_notebook_targetmusic(target['music'])
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

    musicname = values['music_candidates'][0]

    clear_tableselection()

    notebook = get_notebook_targetmusic(musicname)

    targetrecordlist = notebook.get_recordlist(play_mode, difficulty)
    if targetrecordlist is None:
        gui.display_record(None)
        gui.display_image(None)
        return None

    ret = Selection(play_mode, difficulty, musicname, notebook)

    gui.display_record(targetrecordlist)
    image = generateimage_musicinformation(play_mode, difficulty, musicname, targetrecordlist)
    gui.display_image(get_imagevalue(image), others=True)
    ret.selection_scoreinformation(image)

    return ret

def select_history():
    if len(values['history']) != 1:
        return
    
    clear_tableselection()

    timestamp = values['history'][0]
    selection.selection_timestamp(timestamp)
    gui.switch_openfolder_others()

    gui.display_historyresult(selection.get_targetrecordlist(), timestamp)

    if timestamp in results_today.keys():
        display_today(selection)
    else:
        display_history(selection)

def load_resultimages(timestamp, music, playmode, difficulty, recent=False):
    scoretype = {'playmode': playmode, 'difficulty': difficulty}
    image_result = get_resultimage(music, timestamp, setting.imagesave_path, scoretype)
    images_result[timestamp] = image_result
    if image_result is not None:
        timestamps_saved.append(timestamp)

    image_filtered = get_resultimage_filtered(music, timestamp, setting.imagesave_path, scoretype)
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
        load_resultimages(
            selection.timestamp,
            selection.music,
            selection.play_mode,
            selection.difficulty,
            selection.timestamp in notebook_recent.timestamps
        )
    
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
    """画像を保存する
    
    最近のリザルトを選択している場合はリザルト画像を保存する。
    """
    if selection.recent:
        for row_index in table_selected_rows:
            timestamp = list_results[row_index][2]
            if timestamp in results_today.keys() and not timestamp in timestamps_saved:
                save_result(results_today[timestamp], images_result[timestamp])
                notebook_recent.get_result(timestamp)['saved'] = True
                update_resultflag(row_index, saved=True)
        notebook_recent.save()
        refresh_table()
    if selection.image is not None:
        scoretype = {'playmode': selection.play_mode, 'difficulty': selection.difficulty}
        if selection.scoreinformation:
            save_scoreinformationimage(selection.image, selection.music, setting.imagesave_path, scoretype, setting.savefilemusicname_right)
        if selection.graph:
            save_graphimage(selection.image, selection.music, setting.imagesave_path, scoretype, setting.savefilemusicname_right)

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
                load_resultimages(timestamp, target['music'], target['play_mode'], target['difficulty'], True)
            if images_result[timestamp] is not None and not timestamp in images_filtered.keys():
                save_filtered(
                    images_result[timestamp],
                    timestamp,
                    target['music'],
                    target['play_mode'],
                    target['difficulty'],
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
            load_resultimages(selection.timestamp, selection.music, selection.play_mode, selection.difficulty)

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
    
    if not question('確認', upload_confirm_message, window.current_location()):
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

def open_folder_scoreinformations():
    ret = openfolder_scoreinformations(setting.imagesave_path)
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

            if selection.graph or selection.scoreinformation:
                text = text.replace('&&update&&', '')
                text = text.replace('&&option&&', '')
                musics_text.append(text)
                continue

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

            if result['option'] is not None:
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

def view_scoreinformation(selection):
    image = generateimage_musicinformation(
        selection.play_mode,
        selection.difficulty,
        selection.music,
        selection.get_targetrecordlist()
    )

    gui.display_image(get_imagevalue(image), others=True)

    selection.selection_scoreinformation(image)

def create_graph(selection, targetrecord):
    image = create_graphimage(selection.play_mode, selection.difficulty, selection.music, targetrecord)
    if image is None:
        return

    gui.display_image(get_imagevalue(image), others=True)
    
    selection.selection_graph(image)

def summaryimage_generate():
    global image_summary

    image_summary = get_imagevalue(generateimage_summary(
        notebook_summary.count(),
        setting.summaries,
        setting.summary_countmethod_only
    ))

def summaryimage_display():
    gui.display_image(image_summary)

def get_notebook_targetmusic(musicname):
    """目的の曲の記録を取得する

    未ロードの曲の場合はロードする。
    ファイルが見つからない場合は新規のファイルを作成する。

    Args:
        musicname (str): 曲名
    
    Returns:
        (NotebookMusic): 記録データ
    """
    if musicname in notebooks_music.keys():
        return notebooks_music[musicname]

    notebook = NotebookMusic(musicname)
    notebooks_music[musicname] = notebook

    return notebook

def start_hotkeys():
    if setting.hotkeys is None:
        return
    
    if 'display_summaryimage' in setting.hotkeys.keys() and setting.hotkeys['display_summaryimage'] != '':
        keyboard.add_hotkey(setting.hotkeys['display_summaryimage'], summaryimage_display)
    if 'active_screenshot' in setting.hotkeys.keys() and setting.hotkeys['active_screenshot'] != '':
        keyboard.add_hotkey(setting.hotkeys['active_screenshot'], active_screenshot)
    if 'upload_musicselect' in setting.hotkeys.keys() and setting.hotkeys['upload_musicselect'] != '':
        keyboard.add_hotkey(setting.hotkeys['upload_musicselect'], upload_musicselect)

def loading_counter():
    counter = [0, 30]
    def counting(counter):
        while counter[0] < counter[1]:
            time.sleep(3)
            counter[0] += 3
    Thread(target=counting, args=(counter,)).start()
    return counter

if __name__ == '__main__':
    window = gui.generate_window(setting, version)

    display_screenshot_enable = False

    screenshot = Screenshot()

    notebook_recent = NotebookRecent(recent_maxcount)
    notebook_summary = NotebookSummary()
    notebooks_music = {}

    results_today = {}
    timestamps_saved = []
    timestamps_uploaded = []

    images_result = {}
    images_filtered = {}
    imagevalues_result = {}
    imagevalues_filtered = {}

    selection = None

    recent = Recent()

    list_results = []
    table_selected_rows = []

    queue_log = Queue()
    queue_display_image = Queue()
    queue_result_screen = Queue()
    queue_musicselect_screen = Queue()
    queue_functions = Queue()
    queue_messages = Queue()

    storage = StorageAccessor()

    event_close = Event()
    thread = ThreadMain(
        event_close,
        queues = {
            'log': queue_log,
            'display_image': queue_display_image,
            'result_screen': queue_result_screen,
            'musicselect_screen': queue_musicselect_screen,
            'messages': queue_messages
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
        image = Image.open(images_resourcecheck_filepath)
        gui.display_image(get_imagevalue(image))
        Thread(target=check_resource).start()
    else:
        changed = rename_changemusicname()
        queue_functions.put((notebooksummary_startimport, changed))
    
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
                if open_setting(setting, window.current_location()):
                    summaryimage_generate()
                    summaryimage_display()
                window['button_upload'].update(visible=setting.data_collection)
            if event == 'button_save':
                save()
            if event == 'button_filter':
                filter()
            if event == 'button_open_folder_results':
                open_folder_results()
            if event == 'button_open_folder_filtereds':
                open_folder_filtereds()
            if event == 'button_open_folder_scoreinformations':
                open_folder_scoreinformations()
            if event == 'button_open_folder_others':
                if selection.scoreinformation:
                    open_folder_scoreinformations()
                if selection.graph:
                    open_folder_graphs()
            if event == 'button_tweet':
                tweet()
            if event == 'button_export':
                open_export(recent, notebook_summary, window.current_location())
            if event == 'button_upload':
                upload()
            if event == 'table_results':
                if values['table_results'] != table_selected_rows:
                    table_selected_rows = values['table_results']
                    selection_result = select_result_recent()
                    if selection_result is not None:
                        selection = selection_result
                        gui.switch_openfolder_others()
                        if selection.music is not None:
                            window['music_candidates'].update([selection.music], set_to_index=[0])
                        else:
                            window['music_candidates'].update(set_to_index=[])
            if event == 'button_scoreinfotmation':
                if selection is not None and selection.music is not None:
                    view_scoreinformation(selection)
                    gui.switch_openfolder_others('譜面記録')
            if event == 'button_graph':
                if selection is not None and selection.music is not None:
                    create_graph(selection, selection.get_targetrecordlist())
                    gui.switch_openfolder_others('グラフ')
            if event == 'category_versions':
                gui.search_music_candidates()
            if event == 'search_music':
                music_search_time = time.time() + 1
            if event in ['play_mode_sp', 'play_mode_dp', 'difficulty', 'music_candidates']:
                selection = select_music_search()
                gui.switch_openfolder_others('譜面記録')
            if event == '選択した曲の記録を削除する':
                delete_record()
                selection = None
                gui.switch_openfolder_others()
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
                    gui.switch_openfolder_others()
                    gui.display_image(get_imagevalue(queue_display_image.get_nowait()))
                if not queue_result_screen.empty():
                    result_process(queue_result_screen.get_nowait())
                if not queue_musicselect_screen.empty():
                    musicselect_process(queue_musicselect_screen.get_nowait())
                if not queue_functions.empty():
                    func, args = queue_functions.get_nowait()
                    func(args)
                if not queue_messages.empty():
                    message = queue_messages.get_nowait()
                    if message == 'hotkey_start':
                        start_hotkeys()
                    if message == 'hotkey_stop':
                        keyboard.clear_all_hotkeys()
                    if message == 'detect_loading':
                        counter = loading_counter()
                        progress(waitloading_title, waitloading_message, counter, window.current_location())


        except Exception as ex:
            log_debug(ex)
    
    output(notebook_summary)

    window.close()

    del screenshot
