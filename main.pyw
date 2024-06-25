from sys import exit
import keyboard
import time
import PySimpleGUI as sg
from threading import Thread,Event
from queue import Queue
from os.path import join,exists,pardir
import webbrowser
import logging
from urllib import request
from datetime import datetime
from PIL import Image
from urllib.parse import urljoin
from subprocess import Popen
from http.client import HTTPResponse

from setting import Setting

setting = Setting()

if setting.debug:
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
from gui.general import get_imagevalue,message,question
from gui.discord_webhook_setting import open_setting as discord_webhook_setting_open_setting
from define import define
from resources import resource,play_sound_result,check_latest
from screenshot import Screenshot,open_screenimage
from recog import Recognition as recog
from raw_image import save_raw
from storage import StorageAccessor
from record import NotebookRecent,NotebookSummary,NotebookMusic,rename_allfiles,rename_changemusicname,musicnamechanges_filename
from graph import create_graphimage,create_radarchart
from filter import filter as filter_result
from export import (
    Recent,
    output,
    output_notesradarcsv,
    summary_image_filepath,
    notesradar_image_filepath,
    exportimage_musicinformation_filepath,
)
from windows import find_window,get_rect,check_rectsize
from image import (
    save_resultimage,
    save_resultimage_filtered,
    save_scoreinformationimage,
    save_graphimage,
    get_resultimage,
    get_resultimage_filtered,
    generateimage_musictableinformation,
    generateimage_summary,
    generateimage_scoreinformation,
    openfolder_results,
    openfolder_filtereds,
    openfolder_graphs,
    openfolder_scoreinformations,
    openfolder_export,
)
from discord_webhook import post_result,deactivate_allbattles
from result import Result
from notesradar import NotesRadar
from appdata import LocalConfig
import twitter

recent_maxcount = 100

thread_time_wait_nonactive = 1  # INFINITASがアクティブでないときのスレッド周期
thread_time_wait_loading = 30   # INFINITASがローディング中のときのスレッド周期
thread_time_normal = 0.3        # 通常のスレッド周期
thread_time_result = 0.12       # リザルトのときのスレッド周期
thread_time_musicselect = 0.1   # 選曲のときのスレッド周期

windowtitle = 'beatmania IIDX INFINITAS'
exename = 'bm2dx.exe'

upload_confirm_message = [
    u'曲名の誤認識を通報しますか？',
    u'リザルトから曲名を切り取った画像をクラウドにアップロードします。'
]

notebooksummary_confirm_message = [
    u'各曲の記録ファイルから１つのまとめ記録ファイルを作成しています。',
    u'時間がかかる場合がありますが次回からは実行されません。'
]

find_latest_version_message_has_installer = [
    u'最新バージョンが見つかりました。',
    u'インストーラを起動しますか？'
]

find_latest_version_message_not_has_installer = [
    u'最新バージョンが見つかりました。',
    u'リザルト手帳のページを開きますか？'
]

clearrecent_confirm_message = [
    u'exportフォルダのrecent.htmlの内容をリセットしますか？',
]

base_url = 'https://github.com/kaktuswald/inf-notebook/'
releases_url = urljoin(base_url, 'releases/')
latest_url = urljoin(releases_url, 'latest')
wiki_url = urljoin(base_url, 'wiki/')

musicselect_targetrecord = None

discord_server_names = []
discord_webhooks_log = []

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

        if rect is None or rect.right - rect.left == 0 or rect.bottom - rect.top == 0:
            self.queues['log'].put(f'infinitas lost')
            self.sleep_time = thread_time_wait_nonactive

            self.handle = 0
            self.active = False
            screenshot.xy = None
            self.queues['messages'].put('hotkey_stop')

            return

        if not check_rectsize(rect):
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
                self.queues['log'].put(f'detect loading: start waiting: {self.sleep_time}')
                self.queues['messages'].put('detect_loading')
            return
            
        if self.waiting:
            self.waiting = False
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'escape loading: end waiting: {self.sleep_time}')
            self.queues['messages'].put('escape_loading')

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
    def __init__(self, play_mode: str, difficulty: str, music: str, notebook: NotebookMusic):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.music = music
        self.notebook = notebook
        self.timestamp = None
        self.image_graph = None
        self.image_scoreinformation = None
    
    def get_targetrecordlist(self):
        return self.notebook.get_recordlist(self.play_mode, self.difficulty)

def summaryimage_generate():
    global imagevalue_summary

    image = generateimage_summary(
        notebook_summary.count(),
        setting.summaries,
        setting.summary_countmethod_only
    )
    image.save(summary_image_filepath)

    imagevalue_summary = get_imagevalue(image)

def notesradarimage_generate():
    global imagevalue_notesradar

    image = create_radarchart(notesradar)
    image.save(notesradar_image_filepath)

    imagevalue_notesradar = get_imagevalue(image)

def summaryimage_display():
    gui.displayimage(window['image_summary'], imagevalue_summary)

def notesradarimage_display():
    gui.displayimage(window['image_notesradar'], imagevalue_notesradar)

def result_process(screen):
    """リザルトを記録するときの処理をする

    Args:
        screen (Screen): screen.py
    """
    result: Result = recog.get_result(screen)
    if result is None:
        return

    resultimage = screen.original
    if setting.data_collection or force_upload_enable:
        if storage.start_uploadcollection(result, resultimage, force_upload_enable):
            timestamps_uploaded.append(result.timestamp)

    if 'djname' in setting.discord_webhook.keys() and setting.discord_webhook['djname'] is not None and len(setting.discord_webhook['djname']) > 0:
        if 'servers' in setting.discord_webhook.keys() and len(setting.discord_webhook['servers']) > 0:
            Thread(target=post_discord_webhooks, args=(result, resultimage, queue_multimessages)).start()
    
    musicname = result.informations.music

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

    if musicname is not None:
        notebook = get_notebook_targetmusic(musicname)

        notebook.insert(result)
        notebook_summary.import_targetmusic(musicname, notebook)
        notebook_summary.save()

        if result.has_new_record():
            summaryimage_generate()
            summaryimage_display()

            if result.details.score.new:
                if notesradar.insert(
                    result.informations.play_mode,
                    musicname,
                    result.informations.difficulty,
                    result.details.score.current,
                    notebook_summary.json['musics']
                ):
                    update_notesradar()
                    notesradarimage_generate()
                    notesradarimage_display()

    if not result.dead or result.has_new_record():
        recent.insert(result)

    insert_results(result)

def post_discord_webhooks(result: Result, resultimage: Image, queue: Queue):
    imagevalue = None
    imagevalue_filtered_whole = None
    imagevalue_filtered_compact = None
    setting_updated = False
    logs = []
    for settingname, webhooksetting in setting.discord_webhook['servers'].items():
        if webhooksetting['state'] != 'active':
            continue

        if webhooksetting['filter'] == 'none':
            if imagevalue is None:
                if not result.timestamp in imagevalues_result.keys():
                    imagevalues_result[result.timestamp] = get_imagevalue(resultimage)

                imagevalue = imagevalues_result[result.timestamp]
            targetimagevalue = imagevalue
        else:
            if webhooksetting['filter'] == 'whole':
                if imagevalue_filtered_whole is None:
                    imagevalue_filtered_whole = get_imagevalue(filter_result(
                        resultimage,
                        result.play_side,
                        result.rival,
                        result.details.graphtarget == 'rival',
                        False
                    ))
                targetimagevalue = imagevalue_filtered_whole
            if webhooksetting['filter'] == 'compact':
                if imagevalue_filtered_compact is None:
                    imagevalue_filtered_compact = get_imagevalue(filter_result(
                        resultimage,
                        result.play_side,
                        result.rival,
                        result.details.graphtarget == 'rival',
                        True
                    ))
                targetimagevalue = imagevalue_filtered_compact

        postresult, resultmessages = post_result(setting.discord_webhook['djname'], webhooksetting, result, targetimagevalue)
        if postresult is None:
            continue
        
        dt = datetime.now().strftime('%H:%M')
        if postresult:
            if result.informations.music is not None:
                logs.append(f'{dt} {settingname}: {resultmessages}({result.informations.music})')
            else:
                logs.append(f'{dt} {settingname}: {resultmessages}')

            if webhooksetting['mode'] != 'battle':
                if webhooksetting['mode'] == 'score':
                    webhooksetting['mybest'] = result.details.score.current
                if webhooksetting['mode'] == 'misscount':
                    webhooksetting['mybest'] = result.details.miss_count.current
                setting_updated = True
        else:
            webhooksetting['state'] = 'error'
            setting_updated = True
            if resultmessages is str:
                logs.append(f'{dt} {settingname}: {resultmessages}')
            else:
                logs.append(f'{dt} {settingname}: {resultmessages[0]}')
                for line in resultmessages[1:]:
                    logs.append(line)

    if setting_updated:
        setting.save()
        set_discord_servers()
    
    queue.put(('discord_webhooks_log', (logs,)))

def set_discord_servers():
    global discord_server_names
    if 'servers' in setting.discord_webhook.keys():
        discord_server_names = gui.set_discord_servers(setting.discord_webhook['servers'])

def clear_tableselection():
    table_selected_rows = []
    window['table_results'].update(select_rows=table_selected_rows)
    gui.switch_resultsbuttons(False)

def clear_graphimage(imagevalue: bytes):
    gui.displayimage(window['image_graph'], imagevalue)

    window['button_save_graph'].update(disabled=True)
    window['button_post_graph'].update(disabled=True)

def display_graphimage(selection: Selection):
    if selection is None or selection.notebook is None:
        clear_graphimage(resource.imagevalue_imagenothing)
        return
    
    image = create_graphimage(selection.play_mode, selection.difficulty, selection.music, selection.get_targetrecordlist())
    if image is None:
        clear_graphimage(resource.imagevalue_imagenothing)
        return

    gui.displayimage(window['image_graph'], get_imagevalue(image))
    
    selection.image_graph = image

    window['button_save_graph'].update(disabled=False)
    window['button_post_graph'].update(disabled=False)

def clear_scoreinformationimage(imagevalue: bytes):
    gui.displayimage(window['image_scoreinformation'], imagevalue)

    window['button_save_scoreinformation'].update(disabled=True)
    window['button_post_scoreinformation'].update(disabled=True)

def display_scoreinformationimage(selection: Selection) -> Image.Image:
    recordlist = selection.get_targetrecordlist()
    if recordlist is None:
        clear_scoreinformationimage(resource.imagevalue_imagenothing)
        return
    
    image = generateimage_scoreinformation(
        selection.play_mode,
        selection.difficulty,
        selection.music,
        recordlist
    )
    gui.displayimage(window['image_scoreinformation'], get_imagevalue(image))

    selection.image_scoreinformation = image

    window['button_save_scoreinformation'].update(disabled=False)
    window['button_post_scoreinformation'].update(disabled=False)

    return image

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

    ret = Selection(playmode, difficulty, musicname, notebook)

    score = recog.MusicSelect.get_score(np_value)
    if notebook.update_best_musicselect({
        'playmode': playmode,
        'difficulty': difficulty,
        'cleartype': recog.MusicSelect.get_cleartype(np_value),
        'djlevel': recog.MusicSelect.get_djlevel(np_value),
        'score': score,
        'misscount': recog.MusicSelect.get_misscount(np_value),
        'levels': recog.MusicSelect.get_levels(np_value)
    }):
        notebook.save()
        notebook_summary.import_targetmusic(musicname, notebook)
        notebook_summary.save()
        summaryimage_generate()
        summaryimage_display()

        if notesradar.insert(
                playmode,
                musicname,
                difficulty,
                score,
                notebook_summary.json['musics']
            ):
            update_notesradar()
            notesradarimage_generate()
            notesradarimage_display()
    
    clear_tableselection()

    gui.set_search_condition(ret.play_mode, ret.difficulty, ret.music)
    
    musicselect_targetrecord = ret.get_targetrecordlist()
    gui.display_record(musicselect_targetrecord)

    image = display_scoreinformationimage(ret)
    image.save(exportimage_musicinformation_filepath)

    clear_graphimage(resource.imagevalue_graphnogenerate)

    return ret

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

def refresh_table(select_newest=False):
    if select_newest:
        window['table_results'].update(values=list_results, select_rows=[0])
    else:
        window['table_results'].update(values=list_results, select_rows=table_selected_rows)

def insert_recentnotebook_results():
    for timestamp in notebook_recent.timestamps:
        target = notebook_recent.get_result(timestamp)
        if target is None:
            continue
        
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

def insert_results(result: Result):
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

def active_screenshot():
    if not screenshot.shot():
        return
    
    if setting.play_sound:
        play_sound_result()

    image = screenshot.get_image()
    if image is not None:
        filepath = save_raw(image)
        log_debug(f'save screen: {filepath}')
        gui.displayimage(window['image_screenshot'], get_imagevalue(image))
        window['screenshot_filepath'].update(join(pardir, filepath))
    
    window['tab_main_screenshot'].select()

def upload_musicselect():
    """
    選曲画面の一部を学習用にアップロードする
    """
    if not screenshot.shot():
        return
    
    if setting.play_sound:
        play_sound_result()

    image = screenshot.get_image()
    if image is not None:
        storage.start_uploadmusicselect(image)
        log_debug(f'upload screen')
        gui.displayimage(window['image_screenshot'], get_imagevalue(image))
    
    window['tab_main_screenshot'].select()

def log_debug(message):
    logger.debug(message)
    if setting.debug:
        print(message)

def check_latest_version():
    if version == '0.0.0.0':
        return
    
    latest_version = get_latest_version()

    if latest_version == version:
        return
    
    dev = 'dev' in version
    if dev:
        v = version.split('dev')[0]
    else:
        v = version

    splitted_version = [*map(int, v.split('.'))]
    splitted_latest_version = [*map(int, latest_version.split('.'))]
    for i in range(len(splitted_latest_version)):
        if splitted_version[i] > splitted_latest_version[i]:
            return
        if splitted_version[i] < splitted_latest_version[i]:
            break
        
    dev = 'dev' in version
    if dev:
        v = version.split('dev')[0]
    else:
        v = version

    splitted_version = [*map(int, v.split('.'))]
    splitted_latest_version = [*map(int, latest_version.split('.'))]
    for i in range(len(splitted_latest_version)):
        if splitted_version[i] > splitted_latest_version[i]:
            return
        if splitted_version[i] < splitted_latest_version[i]:
            break

    action = None
    config = LocalConfig()
    if config.installer_filepath is not None:
        if config.installer_filepath.exists():
            def action():
                Popen(config.installer_filepath)
                exit()
            message = find_latest_version_message_has_installer
    
    if action is None:
        def action():
            webbrowser.open(wiki_url)
        message = find_latest_version_message_not_has_installer
    
    if question('最新バージョン', message, window.current_location()):
        action()

def get_latest_version():
    with request.urlopen(latest_url) as response:
        response: HTTPResponse
        url = response.geturl()
        version = url.split('/')[-1]
        print(f'released latest version: {version}')
        if version[0] == 'v':
            return version.removeprefix('v')
        else:
            return None

def initialize():
    """初期処理

    別スレッドで実行する

    - リソース画像のロード
    - 曲名の変更に伴う記録ファイルのファイル名変更
    - 必要であれば全曲の記録ファイルを読み出して一つのサマリーファイルを作成する
    - 
    """
    resource.load_images()

    if not setting.ignore_download:
        queue_multimessages.put(('imageinformation_change', (resource.imagevalue_resourcecheck,)))

        check_resource()

    queue_multimessages.put(('imageinformation_change', (resource.imagevalue_summaryprocessing,)))

    if resource.musictable is not None:
        rename_allfiles(resource.musictable['musics'].keys())

    changed = rename_changemusicname()

    if not 'last_allimported' in notebook_summary.json.keys():
        notebook_summary.import_allmusics(version)
        notebook_summary.save()
    else:
        if len(changed) > 0:
            for musicname, renamed in changed:
                del notebook_summary.json['musics'][musicname]
                notebook = get_notebook_targetmusic(renamed)
                notebook_summary.import_targetmusic(renamed, notebook)

            notebook_summary.save()

    notesradar.generate(notebook_summary.json['musics'])

    resource.imagevalue_musictableinformation = get_imagevalue(generateimage_musictableinformation())
    queue_multimessages.put(('imageinformation_change', (resource.imagevalue_musictableinformation,)))

    queue_messages.put('complete_initialize')

def complete_initialize():
    summaryimage_generate()
    notesradarimage_generate()

    summaryimage_display()
    notesradarimage_display()

    window['button_post_summary'].update(disabled=False)
    window['button_post_notesradar'].update(disabled=False)

    if setting.startup_image == 'summary':
        window['tab_main_summary'].select()
    if setting.startup_image == 'notesradar':
        window['tab_main_notesradar'].select()

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

    notesradar_filename = f'{define.notesradar_resourcename}.res'
    if check_latest(storage, notesradar_filename):
        resource.load_resource_notesradar()

    check_latest(storage, musicnamechanges_filename)

    logger.info('complete check resources')

def select_result_recent():
    if len(table_selected_rows) == 0:
        return None

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

    ret.timestamp = timestamp

    if timestamp in results_today.keys():
        display_today(ret)
    else:
        display_history(ret)
    
    if ret.notebook is not None:
        gui.set_search_condition(ret.play_mode, ret.difficulty, ret.music)

        targetrecordlist = ret.get_targetrecordlist()
        gui.display_record(targetrecordlist, timestamp)
        display_scoreinformationimage(ret)
        clear_graphimage(resource.imagevalue_graphnogenerate)

        gui.display_historyresult(targetrecordlist, timestamp)
    else:
        # 何かが認識ミスで譜面が確定していない
        window['music_candidates'].update(set_to_index=[])

        gui.display_record(None)
        clear_scoreinformationimage(None)
        clear_graphimage(None)

    gui.switch_resultsbuttons(True)

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

    ret = Selection(play_mode, difficulty, musicname, notebook)

    gui.display_record(targetrecordlist)
    display_scoreinformationimage(ret)
    clear_graphimage(resource.imagevalue_graphnogenerate)

    return ret

def select_history():
    if len(values['history']) != 1:
        return
    
    clear_tableselection()

    timestamp = values['history'][0]
    selection.timestamp = timestamp

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
    gui.displayimage(window['image_screenshot'], resultimage)

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
        gui.displayimage(window['image_screenshot'], imagevalue_result)
    else:
        if selection.timestamp in imagevalues_filtered.keys():
            imagevalue_filtered = imagevalues_filtered[selection.timestamp]
        else:
            imagevalue_filtered = get_imagevalue(images_filtered[selection.timestamp]) if selection.timestamp in images_filtered.keys() and images_filtered[selection.timestamp] is not None else None
            imagevalues_filtered[selection.timestamp] = imagevalue_filtered

        gui.displayimage(window['image_screenshot'], imagevalue_filtered)

def save_results():
    """画像を保存する
    """
    if len(table_selected_rows) == 0:
        return
    
    for row_index in table_selected_rows:
        timestamp = list_results[row_index][2]
        if timestamp in results_today.keys() and not timestamp in timestamps_saved:
            save_result(results_today[timestamp], images_result[timestamp])
            notebook_recent.get_result(timestamp)['saved'] = True
            update_resultflag(row_index, saved=True)
    notebook_recent.save()
    refresh_table()

def filter_results():
    """ライバル欄にぼかしを入れて、ぼかし画像を表示する

    選択しているすべてのリザルトにぼかし処理を実行する。
    ただし今日のリザルトでない場合は、リザルト画像がファイル保存されている場合のみ、処理が可能。
    """
    if len(table_selected_rows) == 0:
        return
    
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

    if selection.timestamp in imagevalues_filtered.keys():
        imagevalue = imagevalues_filtered[selection.timestamp]
    else:
        filteredimage = images_filtered[selection.timestamp] if selection.timestamp in images_filtered.keys() else None
        imagevalue = get_imagevalue(filteredimage) if filteredimage is not None else None
        if imagevalue is not None:
            imagevalues_filtered[selection.timestamp] = imagevalue

    gui.displayimage(window['image_screenshot'], imagevalue)

def post_results():
    if len(table_selected_rows) == 0:
        return
    
    results = [notebook_recent.get_result(list_results[index][2]) for index in table_selected_rows]
    twitter.post_results(reversed(results))

def upload_results():
    if not setting.data_collection:
        return
    
    if not question('確認', upload_confirm_message, window.current_location()):
        return
    
    for row_index in table_selected_rows:
        timestamp = list_results[row_index][2]
        if timestamp in results_today.keys() and not timestamp in timestamps_uploaded:
            if storage.start_uploadcollection(results_today[timestamp], images_result[timestamp], True):
                timestamps_uploaded.append(timestamp)

def save_scoreinformation():
    """譜面記録画像を保存する
    """
    if selection is None:
        return
    if selection.image_scoreinformation is None:
        return
    
    scoretype = {'playmode': selection.play_mode, 'difficulty': selection.difficulty}
    save_scoreinformationimage(
        selection.image_scoreinformation,
        selection.music,
        setting.imagesave_path,
        scoretype,
        setting.savefilemusicname_right
    )

def save_graph():
    """グラフ画像を保存する
    """
    if selection is None:
        return
    if selection.image_graph is None:
        return
    
    scoretype = {'playmode': selection.play_mode, 'difficulty': selection.difficulty}
    save_graphimage(
        selection.image_graph,
        selection.music,
        setting.imagesave_path,
        scoretype,
        setting.savefilemusicname_right
    )

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

def open_folder_export():
    ret = openfolder_export()
    if ret is not None:
        logger.exception(ret)
        gui.error_message(u'失敗', u'フォルダを開くのに失敗しました。', ret)
    
def open_folder_scoreinformations():
    ret = openfolder_scoreinformations(setting.imagesave_path)
    if ret is not None:
        logger.exception(ret)
        gui.error_message(u'失敗', u'フォルダを開くのに失敗しました。', ret)

def post_scoreinformation():
    if selection is None:
        return
    if selection.notebook is None:
        return
    
    playmode = selection.play_mode
    difficulty = selection.difficulty
    musicname = selection.music

    targetrecord = selection.notebook.get_recordlist(playmode, difficulty)

    if targetrecord is None:
        return

    twitter.post_scoreinformation(playmode, difficulty, musicname, targetrecord)

def clear_selection():
    gui.switch_resultsbuttons(False)
    gui.display_record(None)
    clear_scoreinformationimage(None)
    clear_graphimage(None)

def delete_record():
    if selection is None:
        return

    if selection.music in notebooks_music.keys():
        del notebooks_music[selection.music]

    selection.notebook.delete()
    gui.search_music_candidates()

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
    gui.displayimage(window['image_screenshot'], None)

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
    
    if 'active_screenshot' in setting.hotkeys.keys() and setting.hotkeys['active_screenshot'] != '':
        keyboard.add_hotkey(setting.hotkeys['active_screenshot'], active_screenshot)
    if 'upload_musicselect' in setting.hotkeys.keys() and setting.hotkeys['upload_musicselect'] != '':
        keyboard.add_hotkey(setting.hotkeys['upload_musicselect'], upload_musicselect)

def event_discord_webhook(event: str, values: dict[str, object]) -> bool:
    if not 'servers' in setting.discord_webhook.keys():
        setting.discord_webhook['servers'] = {}
    
    selected_setting = None
    if len(values['discord_webhooks_list']) > 0:
        selected_settingname = discord_server_names[values['discord_webhooks_list'][0]]
        selected_setting = setting.discord_webhook['servers'][selected_settingname]

    if event == 'discord_webhook_savedjname':
        setting.discord_webhook['djname'] = values['discord_webhook_djname']
        setting.save()
    
    if event == 'discord_webhook_add':
        settingname, values = discord_webhook_setting_open_setting(window.current_location())
        if settingname is not None:
            if not settingname in setting.discord_webhook['servers'].keys():
                setting.discord_webhook['servers'][settingname] = values
                setting.save()
                return True
            else:
                message('追加の失敗', '設定名が重複しているため追加できません。', window.current_location())

    if event == 'discord_webhook_update':
        if selected_setting is None:
            return False
        
        settingname, values = discord_webhook_setting_open_setting(
            window.current_location(),
            selected_settingname,
            selected_setting
        )
        if settingname is not None:
            del setting.discord_webhook['servers'][selected_settingname]
            setting.discord_webhook['servers'][settingname] = values
            setting.save()
            return True
        
    if event == 'discord_webhook_activate':
        if selected_setting is None:
            return False
        
        selected_setting['state'] = 'active'
        setting.save()
        return True

    if event == 'discord_webhook_deactivate':
        if selected_setting is None:
            return False
        
        selected_setting['state'] = 'nonactive'
        setting.save()
        return True


    if event == 'discord_webhook_delete':
        if selected_setting is None:
            return

        del setting.discord_webhook['servers'][selected_settingname]
        setting.save()
        return True

    return False

def update_notesradar():
    playmodes = {
        'notesradar_playmode_sp': 'SP',
        'notesradar_playmode_dp': 'DP'
    }

    targetitem = None
    for playmode in playmodes.keys():
        if window[playmode].get():
            targetitem = notesradar.items[playmodes[playmode]]

    if targetitem is None:
        return
    
    window['notesradar_total'].update(targetitem.total)

    if not window['notesradar_attribute'].get() in targetitem.attributes.keys():
        return
    
    targetattribute = targetitem.attributes[window['notesradar_attribute'].get()]

    window['notesradar_value'].update(targetattribute.average)

    rankingtargets = None
    if window['notesradar_tablemode_averagetarget'].get():
        rankingtargets = targetattribute.targets
    if window['notesradar_tablemode_top30'].get():
        rankingtargets = targetattribute.ranking

    if rankingtargets is not None:
        rankingdata = []
        for i in range(len(rankingtargets)):
            targetvalue = rankingtargets[i]
            rankingdata.append([
                i + 1,
                targetvalue.musicname,
                targetvalue.difficulty[0],
                targetvalue.value
            ])
        window['notesradar_ranking'].update(values=rankingdata)

if __name__ == '__main__':
    if 'servers' in setting.discord_webhook.keys():
        deactivate_allbattles(setting.discord_webhook['servers'])

    window = gui.generate_window(setting, version)

    window_debug = None
    if setting.debug:
        window_debug = gui.generate_window_debug()
    
    set_discord_servers()

    detect_infinitas: bool = False
    capture_enable: bool = False

    display_screenshot_enable: bool = False
    force_upload_enable: bool = False

    screenshot = Screenshot()

    notebook_recent = NotebookRecent(recent_maxcount)
    notebook_summary = NotebookSummary()
    notebooks_music = {}

    notesradar = NotesRadar()

    imagevalue_summary = None
    imagevalue_notesradar = None

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
    queue_multimessages = Queue()

    storage = StorageAccessor()

    check_latest_version()

    event_close = Event()
    thread = ThreadMain(
        event_close,
        queues = {
            'log': queue_log,
            'display_image': queue_display_image,
            'result_screen': queue_result_screen,
            'musicselect_screen': queue_musicselect_screen,
            'messages': queue_messages,
            'multimessages': queue_multimessages
        }
    )

    music_search_time = None

    if not setting.has_key('data_collection'):
        setting.data_collection = gui.collection_request('resources/annotation.png')
        setting.save()
        if setting.data_collection:
            window['button_upload_results'].update(visible=True)

    insert_recentnotebook_results()

    Thread(target=initialize, daemon=True).start()
    initializing = True

    while True:
        w, event, values = sg.read_all_windows(timeout=50, timeout_key='timeout')

        try:
            if w is not None and w == window_debug:
                if event == 'text_file_path':
                    if exists(values['text_file_path']):
                        selection = None
                        clear_selection()

                        screen = open_screenimage(values['text_file_path'])
                        gui.displayimage(window['image_screenshot'], get_imagevalue(screen.original))

                        if recog.get_is_savable(screen.np_value):
                            result_process(screen)
                        trimmed = screen.np_value[define.musicselect_trimarea_np]
                        if recog.MusicSelect.get_version(trimmed) is not None:
                            selection_result = musicselect_process(trimmed)
                            if selection_result is not None:
                                selection = selection_result
                if event == 'check_display_screenshot':
                    display_screenshot_enable = values['check_display_screenshot']
                if event == 'force_upload':
                    force_upload_enable = values['force_upload']
                
                continue
            
            if w == window and event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, '終了(X)'):
                if not thread is None:
                    event_close.set()
                    thread.join()
                    log_debug(f'end')
                break

            if event in ['button_openfolder_results', 'リザルト画像フォルダを開く(R)']:
                open_folder_results()
            if event in ['button_openfolder_filtereds', 'ライバル隠し画像フォルダを開く(F)']:
                open_folder_filtereds()
            if event in ['button_openfolder_scoreinformations', '譜面記録画像フォルダを開く(I)']:
                open_folder_scoreinformations()
            if event in ['button_openfolder_graphs', 'グラフ画像フォルダを開く(G)']:
                open_folder_graphs()
            if event in ['button_openfolder_export_summary', 'button_openfolder_export_notesradar', 'エクスポートフォルダを開く(E)']:
                open_folder_export()
            
            if event in ['button_save_results', '画像保存(S)']:
                save_results()
            if event in ['button_filter_results', 'ライバルを隠す(F)']:
                filter_results()
            if event in ['button_post_results', 'Xにポスト(P)']:
                post_results()
            if event == 'button_upload_results':
                upload_results()

            if event in ['image_graph', 'グラフ画像の作成(C)']:
                display_graphimage(selection)
            if event in ['button_save_scoreinformation', '譜面記録画像の保存(I)']:
                save_scoreinformation()
            if event in ['button_save_graph', 'グラフ画像の保存(G)']:
                save_graph()
            if event in ['button_post_scoreinformation', 'button_post_graph', '譜面記録のポスト(P)']:
                post_scoreinformation()

            if event in ['button_setting', 'button_summary_setting', '設定を開く(S)']:
                if open_setting(setting, window.current_location(), event == 'button_summary_setting'):
                    summaryimage_generate()
                    summaryimage_display()
                window['button_upload_results'].update(visible=setting.data_collection)
            if event in ['button_export', 'エクスポートを開く(E)']:
                open_export(recent, notebook_summary, window.current_location())
            if event == 'CSV出力(P)':
                output(notebook_summary)
                output_notesradarcsv(notesradar)
                message('完了', '出力が完了しました。', window.current_location())
            if event == '最近のデータのリセット(R)':
                if question('確認', clearrecent_confirm_message, window.current_location()):
                    recent.clear()
            
            if event == 'button_post_summary':
                twitter.post_summary(notebook_summary)
            if event == 'button_post_notesradar':
                twitter.post_notesradar(notesradar)

            if event == 'button_summary_switch':
                setting.summary_countmethod_only = not setting.summary_countmethod_only
                setting.save()
                summaryimage_generate()
                summaryimage_display()
                
            if event == 'table_results':
                if values['table_results'] != table_selected_rows:
                    table_selected_rows = values['table_results']
                    selection_result = select_result_recent()
                    if selection_result is not None:
                        selection = selection_result
            
            if event == 'category_versions':
                gui.search_music_candidates()
            if event == 'search_music':
                music_search_time = time.time() + 1
            if event in ['play_mode_sp', 'play_mode_dp', 'difficulty', 'music_candidates']:
                selection = select_music_search()
            if event == 'delete_selectmusic':
                delete_record()
                selection = None
                clear_selection()
            if event == 'history':
                select_history()
            if event == 'delete_selectresult':
                delete_targetrecord()

            if event == 'button_best_switch':
                gui.switch_best_display()
            
            if 'discord_webhook' in event:
                if event_discord_webhook(event, values):
                    set_discord_servers()
            
            if 'notesradar' in event:
                update_notesradar()
            
            if event == 'timeout':
                if not detect_infinitas and thread.handle:
                    detect_infinitas = True
                    gui.switch_textcolor(window['detect_infinitas'], True)
                if detect_infinitas and not thread.handle:
                    detect_infinitas = False
                    gui.switch_textcolor(window['detect_infinitas'], False)
                if not capture_enable and screenshot.xy:
                    capture_enable = True
                    gui.switch_textcolor(window['capture_enable'], True)
                if capture_enable and not screenshot.xy:
                    capture_enable = False
                    gui.switch_textcolor(window['capture_enable'], False)
                
                if music_search_time is not None and time.time() > music_search_time:
                    music_search_time = None
                    gui.search_music_candidates()
                
                if not queue_log.empty():
                    log_debug(queue_log.get_nowait())
                if not queue_display_image.empty():
                    clear_tableselection()
                    window['music_candidates'].update(set_to_index=[])
                    selection = None
                    clear_selection()
                    gui.displayimage(window['image_screenshot'], get_imagevalue(queue_display_image.get_nowait()))
                if not queue_result_screen.empty():
                    result_process(queue_result_screen.get_nowait())
                if not queue_musicselect_screen.empty():
                    selection_result = musicselect_process(queue_musicselect_screen.get_nowait())
                    if selection_result is not None:
                        selection = selection_result
                if not queue_functions.empty():
                    func, args = queue_functions.get_nowait()
                    func(args)
                if not queue_messages.empty():
                    queuemessage = queue_messages.get_nowait()
                    if queuemessage == 'complete_initialize':
                        complete_initialize()
                        initializing = False
                    if queuemessage == 'hotkey_start':
                        start_hotkeys()
                    if queuemessage == 'hotkey_stop':
                        keyboard.clear_all_hotkeys()
                    if queuemessage == 'detect_loading':
                        gui.displayimage(window['image_information'], resource.imagevalue_loading)
                        window['tab_main_information'].select()
                    if queuemessage == 'escape_loading':
                        gui.displayimage(window['image_information'], resource.imagevalue_musictableinformation)
                        if setting.startup_image == 'summary':
                            window['tab_main_summary'].select()
                        if setting.startup_image == 'notesradar':
                            window['tab_main_notesradar'].select()
                if not queue_multimessages.empty():
                    queuemessage, args = queue_multimessages.get_nowait()
                    if queuemessage == 'imageinformation_change':
                        gui.displayimage(window['image_information'], args[0])
                    if queuemessage == 'discord_webhooks_log':
                        discord_webhooks_log.extend(args[0])
                        del discord_webhooks_log[:-6]
                        window['discord_webhooks_log'].update(values=discord_webhooks_log)

        except Exception as ex:
            log_debug(ex)
    
    output(notebook_summary)
    output_notesradarcsv(notesradar)

    window.close()

    del screenshot
