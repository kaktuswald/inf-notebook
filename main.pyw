import keyboard
import time
from threading import Thread,Event
from queue import Queue,Full
import webbrowser
import logging
from urllib import request
from datetime import datetime,timezone
from PIL import Image
from urllib.parse import urljoin
from subprocess import Popen
from http.client import HTTPResponse
from os.path import abspath,isfile
from json import dump,dumps,load,loads
from uuid import uuid1
from base64 import b64decode,b64encode
from webui import webui
from sys import exit

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
from general import get_imagevalue,save_imagevalue,imagesize
from define import Playmodes,define
from resources import resource,play_sound_result,check_latest
from screenshot import Screen,Screenshot
from recog import Recognition as recog
from raw_image import save_raw
from storage import StorageAccessor
from record import NotebookRecent,NotebookSummary,Notebooks,rename_allfiles,rename_changemusicname,musicnamechanges_filename
from filter import filter as filter_result
from export import (
    Recent,
    output,
    output_notesradarcsv,
    generate_exportsettingcss,
    export_dirname,
    summary_image_filepath,
    notesradar_image_filepath,
    exportimage_musicinformation_filepath,
    csssetting_filepath,
)
from windows import find_window,get_rect,check_rectsize,gethandle,show_messagebox,change_window_setting
import image
from image import (
    save_resultimage,
    save_resultimage_filtered,
    get_resultimage,
    get_resultimage_filtered,
    openfolder_results,
    openfolder_filtereds,
    openfolder_scorecharts,
    openfolder_scoreinformations,
    openfolder_export,
)
from discord_webhook import filtereds as discordwebhook_filtereds
from discord_webhook import post_test,post_registered,post_result
from result import Result,RecentResult
from notesradar import NotesRadar
from appdata import LocalConfig
import twitter
from socket_server import SocketServer

windowtitle = f'インフィニタス リザルト手帳'

recent_maxcount = 100

thread_time_wait_nonactive = 1  # INFINITASがアクティブでないときのスレッド周期
thread_time_wait_loading = 30   # INFINITASがローディング中のときのスレッド周期
thread_time_normal = 0.3        # 通常のスレッド周期
thread_time_result = 0.12       # リザルトのときのスレッド周期
thread_time_musicselect = 0.1   # 選曲のときのスレッド周期

gamewindowtitle = 'beatmania IIDX INFINITAS'
exename = 'bm2dx.exe'

notebooksummary_confirm_message = [
    u'各曲の記録ファイルから１つのまとめ記録ファイルを作成しています。',
    u'時間がかかる場合がありますが次回からは実行されません。'
]

find_latest_version_message_has_installer = u'インストーラを起動しますか？'
find_latest_version_message_not_has_installer = u'リザルト手帳のページを開きますか？'

base_url = 'https://github.com/kaktuswald/inf-notebook/'
releases_url = urljoin(base_url, 'releases/')
latest_url = urljoin(releases_url, 'latest')
wiki_url = urljoin(base_url, 'wiki/')

class ThreadMain(Thread):
    handle: int = 0
    active: bool = False
    waiting: bool = False
    musicselect: bool = False
    confirmed_somescreen: bool = False
    confirmed_processable: bool = False
    processed: bool = False
    screen_latest = None

    def __init__(self, event_close: Event, queues: dict[str, Queue]):
        self.event_close = event_close
        self.queues = queues

        Thread.__init__(self)

    def run(self):
        self.sleep_time = thread_time_wait_nonactive
        self.queues['log'].put('start thread')
        while not self.event_close.wait(timeout=self.sleep_time):
            self.routine()

    def routine(self):
        if self.handle == 0:
            self.handle = find_window(gamewindowtitle, exename)
            if self.handle == 0:
                return

            self.queues['log'].put(f'infinitas find')
            api.send_message('switch_detect_infinitas', True)
            self.active = False
            screenshot.xy = None
        
        rect = get_rect(self.handle)

        if rect is None or rect.right - rect.left == 0 or rect.bottom - rect.top == 0:
            self.queues['log'].put(f'infinitas lost')
            api.send_message('switch_detect_infinitas', False)
            api.send_message('switch_capturable', False)
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
                api.send_message('switch_capturable', False)
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
            api.send_message('switch_capturable', True)
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
        
        if screen != 'music_select' and self.musicselect:
            # 画面が選曲から抜けたとき
            self.musicselect = False
            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'screen out music select: {self.sleep_time}')

        shotted = False
        if screen == 'music_select':
            if not self.musicselect:
                # 画面が選曲に入ったとき
                self.musicselect = True
                self.sleep_time = thread_time_musicselect
                self.queues['log'].put(f'screen in music select: {self.sleep_time}')

            screenshot.shot()
            shotted = True

            trimmed = screenshot.np_value[define.musicselect_trimarea_np]
            if recog.MusicSelect.get_version(trimmed) is not None:
                try:
                    self.queues['musicselect_screen'].put(trimmed, block=False)
                except Full as ex:
                    pass

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

        if time.time() - self.find_time <= thread_time_normal * 2 - 0.1:
            return

        if screen == 'result':
            resultscreen = screenshot.get_resultscreen()

            try:
                self.queues['result_screen'].put(resultscreen, block=False)
            except Full as ex:
                pass

            self.sleep_time = thread_time_normal
            self.queues['log'].put(f'processing result screen: {self.sleep_time}')
            self.processed = True

class GuiApi():
    '''メイン画面のAPIクラス
    '''
    window: webui.Window
    notebooks: Notebooks

    findnewestversionaction: object = None
    image_activescreenshot: bytes = None
    image_scoreinformation: dict[str, str|bytes] = None
    image_scoregraph: dict[str, str|bytes] = None

    @staticmethod
    def get_version(event: Event):
        event.return_string(version)

    @staticmethod
    def get_imagesize(event: Event):
        event.return_string(dumps(imagesize))

    @staticmethod
    def get_playmodes(event: Event):
        event.return_string(dumps(Playmodes.values))

    @staticmethod
    def get_difficulties(event: Event):
        event.return_string(dumps(define.value_list['difficulties']))

    @staticmethod
    def get_levels(event: Event):
        event.return_string(dumps(define.value_list['levels']))

    @staticmethod
    def get_cleartypes(event: Event):
        event.return_string(dumps(define.value_list['clear_types']))

    @staticmethod
    def get_djlevels(event: Event):
        event.return_string(dumps(define.value_list['dj_levels']))

    @staticmethod
    def get_notesradar_attributes(event: Event):
        event.return_string(dumps(define.value_list['notesradar_attributes']))

    @staticmethod
    def checkresource(event: webui.Event):
        '''リソースファイルのチェック
        '''
        if not setting.ignore_download:
            check_resource()

    @staticmethod
    def execute_records_processing(event: webui.Event):
        initial_records_processing()
    
    @staticmethod
    def execute_generate_notesradar(event: webui.Event):
        notesradar.generate(notebook_summary.json['musics'])

    @staticmethod
    def start_capturing(event: webui.Event):
        if not thread.is_alive():
            thread.start()

    @staticmethod
    def get_resource_musictable(event: webui.Event):
        event.return_string(dumps(resource.musictable))
    
    @staticmethod
    def get_resource_notesradar(event: webui.Event):
        event.return_string(dumps(resource.notesradar))
    
    def __init__(self, window: webui.Window, notebooks: Notebooks):
        self.window = window
        self.notebooks = notebooks

        window.bind('get_version', GuiApi.get_version)

        window.bind('get_imagesize', GuiApi.get_imagesize)

        window.bind('get_playmodes', GuiApi.get_playmodes)
        window.bind('get_difficulties', GuiApi.get_difficulties)
        window.bind('get_levels', GuiApi.get_levels)
        window.bind('get_cleartypes', GuiApi.get_cleartypes)
        window.bind('get_djlevels', GuiApi.get_djlevels)
        window.bind('get_notesradar_attributes', GuiApi.get_notesradar_attributes)

        window.bind('checkresource', GuiApi.checkresource)
        window.bind('execute_records_processing', GuiApi.execute_records_processing)
        window.bind('execute_generate_notesradar', GuiApi.execute_generate_notesradar)
        window.bind('start_capturing', GuiApi.start_capturing)
        window.bind('getresource_musictable', GuiApi.get_resource_musictable)
        window.bind('getresource_notesradar', GuiApi.get_resource_notesradar)

        window.bind('get_setting', self.get_setting)
        window.bind('save_setting', self.save_setting)

        window.bind('get_recentnotebooks', self.get_recentnotebooks)

        window.bind('get_discordwebhook_settings', self.get_discordwebhook_settings)

        window.bind('check_latestversion', self.check_latestversion)

        window.bind('upload_imagenothingimage', self.upload_imagenothingimage)
        window.bind('upload_informationimage', self.upload_informationimage)
        window.bind('upload_summaryimage', self.upload_summaryimage)
        window.bind('upload_notesradarimage', self.upload_notesradarimage)
        window.bind('upload_scoreinformationimage', self.upload_scoreinformationimage)
        window.bind('upload_scoregraphimage', self.upload_scoregraphimage)

        window.bind('save_scoreinformationimage', self.save_scoreinformationimage)
        window.bind('save_scoregraphimage', self.save_scoregraphimage)

        window.bind('post_summary', self.post_summary)
        window.bind('post_notesradar', self.post_notesradar)
        window.bind('post_scoreinformation', self.post_scoreinformation)

        window.bind('openfolder_export', self.openfolder_export)
        window.bind('openfolder_results', self.openfolder_results)
        window.bind('openfolder_filtereds', self.openfolder_filtereds)
        window.bind('openfolder_scoreinformations', self.openfolder_scoreinformations)
        window.bind('openfolder_scorecharts', self.openfolder_scorecharts)

        window.bind('get_summaryvalues', self.get_summaryvalues)

        window.bind('get_activescreenshot', self.get_activescreenshot)

        window.bind('get_notesradar_chartvalues', self.get_notesradar_chartvalues)
        window.bind('get_notesradar_total', self.get_notesradar_total)
        window.bind('get_notesradar_ranking', self.get_notesradar_ranking)

        window.bind('switch_displayresultimage', self.switch_displayresultimage)
        window.bind('switch_summarycountmethod', self.switch_summarycountmethod)

        window.bind('get_resultimage', self.get_resultimage)
        window.bind('get_resultimage_filtered', self.get_resultimage_filtered)

        window.bind('get_scoreresult', self.get_scoreresult)
        window.bind('get_playresult', self.get_playresult)
        
        window.bind('recents_save_resultimages', self.recents_save_resultimages)
        window.bind('recents_save_resultimages_filtered', self.recents_save_resultimages_filtered)

        window.bind('recents_post_results', self.recents_post_results)
        window.bind('recents_upload_collectionimages', self.recents_upload_collectionimages)

        window.bind('delete_musicresult', self.delete_musicresult)
        window.bind('delete_scoreresult', self.delete_scoreresult)
        window.bind('delete_playresult', self.delete_playresult)

        window.bind('execute_findnewestversionaction', self.execute_findnewestversionaction)

        window.bind('output_csv', self.output_csv)
        window.bind('clear_recent', self.clear_recent)

    def get_setting(self, event: webui.Event):
        '''現在の設定の取得
        '''
        event.return_string(dumps(setting.json))
    
    def save_setting(self, event: webui.Event):
        values = loads(event.get_string_at(0))

        setting.newrecord_only = values['newrecord_only']
        setting.play_sound = values['play_sound']
        setting.autosave = values['autosave']
        setting.autosave_filtered = values['autosave_filtered']
        setting.filter_compact = values['filter_compact']
        setting.savefilemusicname_right = values['savefilemusicname_right']

        setting.hotkeys['active_screenshot'] = values['hotkeys']['active_screenshot']
        setting.hotkeys['upload_musicselect'] = values['hotkeys']['upload_musicselect']
        setting.hotkeys['select_summary'] = values['hotkeys']['select_summary']
        setting.hotkeys['select_notesradar'] = values['hotkeys']['select_notesradar']
        setting.hotkeys['select_screenshot'] = values['hotkeys']['select_screenshot']
        setting.hotkeys['select_scoreinformation'] = values['hotkeys']['select_scoreinformation']
        setting.hotkeys['select_scoregraph'] = values['hotkeys']['select_scoregraph']

        setting.summary_countmethod_only = values['summary_countmethod_only']
        setting.display_result = values['display_result']
        setting.resultimage_filtered = values['resultimage_filtered']
        setting.imagesave_path = values['imagesave_path']
        setting.startup_image = values['startup_image']
        setting.hashtags = values['hashtags']
        setting.data_collection = values['data_collection']

        for playmode, playmodevalues in setting.summaries.items():
            for level, levelvalues in playmodevalues.items():
                levelvalues['cleartypes'] = []
                levelvalues['djlevels'] = []
                for cleartype in values['summaries'][playmode][level]['cleartypes']:
                    levelvalues['cleartypes'].append(cleartype)
                for djlevel in values['summaries'][playmode][level]['djlevels']:
                    levelvalues['djlevels'].append(djlevel)

        if values['port']['main'].isdigit():
            mainport = int(values['port']['main'])
            if mainport > 1024:
                setting.port['main'] = mainport
        if values['port']['socket'].isdigit():
            socketport = int(values['port']['socket'])
            if socketport > 1024:
                setting.port['socket'] = socketport

        setting.save()

        generate_exportsettingcss(setting.port['socket'])

    def get_recentnotebooks(self, event: webui.Event):
        ret = [result.encode() for result in recentresults]

        event.return_string(dumps(ret))
    
    def get_discordwebhook_settings(self, event: webui.Event):
        event.return_string(dumps(setting.discord_webhook['joinedevents']))
    
    def check_latestversion(self, event: webui.Event):
        '''最新バージョンをチェックする
        
        最新バージョンが存在するなら、該当するアクションを実行するかをユーザに尋ねる
        '''
        message, action = check_latest_version()

        self.findnewestversionaction = action

        event.return_string(dumps(message))
    
    def upload_imagenothingimage(self, event: webui.Event):
        '''画像なし画像のアップロード
        
        Socketサーバを経由してインフォメーション画像を更新する。
        Args:
            data(str): エンコードされた画像データ
        '''
        data = event.get_string_at(0)

        decorded_data = b64decode(data)

        socket_server.imagevalue_imagenothing = decorded_data
        socket_server.update_information(decorded_data)
    
    def upload_informationimage(self, event: webui.Event):
        '''インフォメーション画像のアップロード
        
       Socketサーバを経由して更新する。
        Args:
            data(str): エンコードされた画像データ
        '''
        data = event.get_string_at(0)

        decorded_data = b64decode(data)

        socket_server.update_information(decorded_data)

    def upload_summaryimage(self, event: webui.Event):
        '''統計画像のアップロード
        
        ファイルに保存する。Socketサーバを経由して更新する。
        Args:
            data(str): エンコードされた画像データ
        '''
        data = event.get_string_at(0)

        decorded_data = b64decode(data)

        socket_server.update_summary(decorded_data)

        save_imagevalue(decorded_data, summary_image_filepath)
        self.send_message('append_log', 'saved summary.png')

    def upload_notesradarimage(self, event: webui.Event):
        '''ノーツレーダー画像のアップロード
        
        ファイルに保存する。Socketサーバを経由して更新する。
        Args:
            data(str): エンコードされた画像データ
        '''
        data = event.get_string_at(0)

        decorded_data = b64decode(data)

        socket_server.update_notesradar(decorded_data)

        save_imagevalue(decorded_data, notesradar_image_filepath)
        self.send_message('append_log', 'saved notesradar.png')

    def upload_scoreinformationimage(self, event: webui.Event):
        '''譜面情報画像のアップロード
        
        ファイルに保存する。Socketサーバを経由して更新する。
        Args:
            data(str): エンコードされた画像データ
            playmode(str): プレイモード(SP or DP)
            musicname(str): 曲名
            difficulty(str): 譜面難易度
        '''
        data = event.get_string_at(0)
        playmode = event.get_string_at(1)
        musicname = event.get_string_at(2)
        difficulty = event.get_string_at(3)

        decorded_value = b64decode(data)

        self.image_scoreinformation = {
            'playmode': playmode,
            'musicname': musicname,
            'difficulty': difficulty,
            'imagevalue': decorded_value,
        }

        socket_server.update_scoreinformation(decorded_value)

        save_imagevalue(decorded_value, exportimage_musicinformation_filepath)
        self.send_message('append_log', 'saved musicinformation.png')

    def upload_scoregraphimage(self, event: webui.Event):
        '''譜面グラフ画像のアップロード
        
        Socketサーバを経由して更新する。
        未実装だがファイルに保存しても良いかもしれない。
        Args:
            data(str): エンコードされた画像データ
            playmode(str): プレイモード(SP or DP)
            musicname(str): 曲名
            difficulty(str): 譜面難易度
        '''
        data = event.get_string_at(0)
        playmode = event.get_string_at(1)
        musicname = event.get_string_at(2)
        difficulty = event.get_string_at(3)

        decorded_data = b64decode(data)

        self.image_scoregraph = {
            'playmode': playmode,
            'musicname': musicname,
            'difficulty': difficulty,
            'imagevalue': decorded_data,
        }

        socket_server.update_scoregraph(decorded_data)

    def save_scoreinformationimage(self, event: webui.Event):
        '''譜面記録画像をファイルに保存する
        
        保存ボタンを押したときに実行する。
        '''
        playmode = event.get_string_at(0)
        musicname = event.get_string_at(1)
        difficulty = event.get_string_at(2)

        if self.image_scoreinformation is None:
            event.return_string(dumps(False))
            return
        
        if self.image_scoreinformation['imagevalue'] is None:
            event.return_string(dumps(False))
            return

        if self.image_scoreinformation['playmode'] != playmode:
            event.return_string(dumps(False))
            return
        if self.image_scoreinformation['musicname'] != musicname:
            event.return_string(dumps(False))
            return
        if self.image_scoreinformation['difficulty'] != difficulty:
            event.return_string(dumps(False))
            return
        
        filepath = image.get_scoreinformationimagepath(
            self.image_scoregraph['playmode'],
            self.image_scoregraph['musicname'],
            self.image_scoregraph['difficulty'],
            setting.imagesave_path,
            setting.savefilemusicname_right,
        )

        save_imagevalue(self.image_scoreinformation['imagevalue'], filepath)
        self.send_message('append_log', 'saved scoreinformation.png')

        event.return_string(dumps(True))

    def save_scoregraphimage(self, event: webui.Event):
        '''譜面グラフ画像をファイル保存する
        
        保存ボタンを押したときに実行。
        Args:
            playmode(str): プレイモード(SP or DP)
            musicname(str): 曲名
            difficulty(str): 譜面難易度
        '''
        playmode = event.get_string_at(0)
        musicname = event.get_string_at(1)
        difficulty = event.get_string_at(2)

        if self.image_scoregraph is None:
            event.return_string(dumps(False))
            return

        if self.image_scoregraph['playmode'] != playmode:
            event.return_string(dumps(False))
            return
        if self.image_scoregraph['musicname'] != musicname:
            event.return_string(dumps(False))
            return
        if self.image_scoregraph['difficulty'] != difficulty:
            event.return_string(dumps(False))
            return
        
        filepath = image.get_scoregraphimagepath(
            self.image_scoregraph['playmode'],
            self.image_scoregraph['musicname'],
            self.image_scoregraph['difficulty'],
            setting.imagesave_path,
            setting.savefilemusicname_right,
        )

        save_imagevalue(self.image_scoregraph['imagevalue'], filepath)
        self.send_message('append_log', 'saved scoregraph.png')

        event.return_string(dumps(True))

    def post_summary(self, event: webui.Event):
        twitter.post_summary(notebook_summary, setting.hashtags)
    
    def post_notesradar(self, event: webui.Event):
        twitter.post_notesradar(notesradar, setting.hashtags)

    def post_scoreinformation(self, event: webui.Event):
        '''譜面情報をポストする

        Args:
            musicname(str): 曲名
            playmode(str): プレイモード(SP or DP)
            difficulty(str): 難易度
            timestamp(str): タイムスタンプ
        '''
        playmode = event.get_string_at(0)
        musicname = event.get_string_at(1)
        difficulty = event.get_string_at(2)

        targetrecord = notebooks_music.get_notebook(musicname).get_scoreresult(playmode, difficulty)

        if targetrecord is None:
            return

        twitter.post_scoreinformation(playmode, difficulty, musicname, targetrecord, setting.hashtags)

    def openfolder_export(self, event: webui.Event):
        '''エクスポートフォルダを開く
        '''
        event.return_bool(openfolder_export())
    
    def openfolder_results(self, event: webui.Event):
        '''リザルト画像の出力先フォルダを開く
        '''
        event.return_bool(openfolder_results(setting.imagesave_path))

    def openfolder_filtereds(self, event: webui.Event):
        '''ライバルを隠したリザルト画像の出力先フォルダを開く
        '''
        event.return_bool(openfolder_filtereds(setting.imagesave_path))

    def openfolder_scoreinformations(self, event: webui.Event):
        '''譜面情報画像の出力先フォルダを開く
        '''
        event.return_bool(openfolder_scoreinformations(setting.imagesave_path))

    def openfolder_scorecharts(self, event: webui.Event):
        '''グラフ画像の出力先フォルダを開く
        '''
        event.return_bool(openfolder_scorecharts(setting.imagesave_path))

    def get_summaryvalues(self, event: webui.Event):
        counts = notebook_summary.count()

        result = {}
        for playmode in setting.summaries.keys():
            result[playmode] = {}
            for level in setting.summaries[playmode].keys():
                result[playmode][level] = {
                    'TOTAL': counts[playmode][level]['total'],
                    'NO DATA': counts[playmode][level]['total'] - counts[playmode][level]['datacount'],
                }

                for summarykey, targetkey in [('cleartypes', 'clear_types'), ('djlevels', 'dj_levels')]:
                    result[playmode][level][summarykey] = {}
                    for key in setting.summaries[playmode][level][summarykey]:
                        if not setting.summary_countmethod_only:
                            index = define.value_list[targetkey].index(key)
                            result[playmode][level][summarykey][key] = sum([counts[playmode][level][k] for k in define.value_list[targetkey][index:]])
                        else:
                            result[playmode][level][summarykey][key] = counts[playmode][level][key]
        
        event.return_string(dumps(result))

    def get_activescreenshot(self, event: webui.Event):
        decorded_data = b64encode(self.image_activescreenshot).decode('utf-8')
        event.return_string(dumps(decorded_data))

    def get_notesradar_chartvalues(self, event: webui.Event):
        '''ノーツレーダーのチャート値を返す
        '''
        ret = {}
        for playmode, playmodeitem in notesradar.items.items():
            ret[playmode] = {}
            for attribute, attributeitem in playmodeitem.attributes.items():
                ret[playmode][attribute] = attributeitem.average
        
        event.return_string(dumps(ret))

    def get_notesradar_total(self, event: webui.Event):
        '''ノーツレーダーの合計値を返す
        
        Args:
            playmode(str): 対象のプレイモード(SP or DP)
        Returns:
            float: 対象のプレイモードの合計値
        '''
        playmode = event.get_string_at(0)

        event.return_string(dumps(notesradar.items[playmode].total))
    
    def get_notesradar_ranking(self, event: webui.Event):
        '''ノーツレーダーの合計値を返す
        
        表示リストモードがaveragetargetの場合、平均値計算対象の10譜面を返す。
        topの場合はノーツレーダー値上位50譜面を返す。
        Args:
            playmode(str): 対象のプレイモード(SP or DP)
            attribute(str): 対象の要素(NOTESとか)
            tablemode(str): 表示リストモード(averagetarget or tops)
        Returns:
            float: 対象のプレイモードの合計値
        '''
        playmode = event.get_string_at(0)
        attribute = event.get_string_at(1)
        tablemode = event.get_string_at(2)

        targetplaymode = notesradar.items[playmode]

        targetattribute = targetplaymode.attributes[attribute]
        targets = None
        if tablemode == 'averagetarget':
            targets = targetattribute.targets
        if tablemode == 'tops':
            targets = targetattribute.ranking
        
        if targets is None:
            event.return_string(dumps(None))
            return
        
        ret = []
        for i in range(len(targets)):
            ret.append({
                'rank': i + 1,
                'musicname': targets[i].musicname,
                'difficulty': targets[i].difficulty,
                'value': targets[i].value,
            })
        
        event.return_string(dumps(ret))
    
    def switch_displayresultimage(self, event: webui.Event):
        '''表示するリザルト画像のライバルぼかし設定を切り替える
        '''
        setting.resultimage_filtered = not setting.resultimage_filtered
        setting.save()

    def switch_summarycountmethod(self, event: webui.Event):
        '''統計のカウント方式を切り替える
        
        「達成している曲数のカウント」<==>「対象の曲数のみのカウント」
        '''
        setting.summary_countmethod_only = not setting.summary_countmethod_only
        setting.save()

    def get_resultimage(self, event: webui.Event):
        '''リザルト画像を表示する

        まずファイルからのロードを試みる。
        画像から画像データの取得を試みる。
        リザルト画像データがあるならそれを表示する、なければぼかしつきリザルト画像データの有無を確認し、表示する。
        Args:
            musicname(str): 曲名
            playmode(str): プレイモード(SP or DP)
            difficulty(str): 難易度
            timestamp(str): タイムスタンプ
        Returns:
            str: デコードされた画像データ
        '''
        musicname = event.get_string_at(0)
        playmode = event.get_string_at(1)
        difficulty = event.get_string_at(2)
        timestamp = event.get_string_at(3)

        if not timestamp in images_result.keys():
            load_resultimages(playmode, musicname, difficulty, timestamp, timestamp in notebook_recent.timestamps)
        
        if not timestamp in imagevalues_result:
            if images_result[timestamp] is not None:
                imagevalue = get_imagevalue(images_result[timestamp])
            else:
                imagevalue = None
            
            imagevalues_result[timestamp] = imagevalue
        else:
            imagevalue = imagevalues_result[timestamp]

        if imagevalue is None:
            if timestamp in imagevalues_filtered.keys():
                imagevalue = imagevalues_filtered[timestamp]
            else:
                if timestamp in images_filtered.keys():
                    imagevalue = get_imagevalue(images_filtered[timestamp])
                    imagevalues_filtered[timestamp] = imagevalue

        if imagevalue is not None:
            socket_server.update_screenshot(imagevalue)
            decorded_data = b64encode(imagevalue).decode('utf-8')
            event.return_string(dumps(decorded_data))
            return
        
        socket_server.update_screenshot(None)
        event.return_string(dumps(None))
    
    def get_resultimage_filtered(self, event: webui.Event):
        '''ぼかしの入ったリザルト画像を表示する

        Args:
            musicname(str): 曲名
            playmode(str): プレイモード(SP or DP)
            difficulty(str): 難易度
            timestamp(str): タイムスタンプ
        Returns:
            str: デコードされた画像データ
        '''
        musicname = event.get_string_at(0)
        playmode = event.get_string_at(1)
        difficulty = event.get_string_at(2)
        timestamp = event.get_string_at(3)

        if not timestamp in images_result.keys():
            load_resultimages(playmode, musicname, difficulty, timestamp, timestamp in notebook_recent.timestamps)
        
        if not timestamp in imagevalues_filtered.keys():
            if not timestamp in images_filtered.keys() and timestamp in images_result.keys():
                target = notebook_recent.get_result(timestamp)
                if target is not None:
                    images_filtered[timestamp] = filter_result(
                        images_result[timestamp],
                        target['play_side'],
                        target['has_loveletter'],
                        target['has_graphtargetname'],
                        setting.filter_compact,
                    )

            if images_filtered[timestamp] is not None:
                imagevalue = get_imagevalue(images_filtered[timestamp])
            else:
                imagevalue = None
            
            imagevalues_filtered[timestamp] = imagevalue
        else:
            imagevalue = imagevalues_filtered[timestamp]

        if imagevalue is not None:
            socket_server.update_screenshot(imagevalue)
            decorded_data = b64encode(imagevalue).decode('utf-8')
            event.return_string(dumps(decorded_data))
            return

        socket_server.update_screenshot(None)
        event.return_string(dumps(None))

    def get_scoreresult(self, event: webui.Event):
        '''対象の譜面の記録を返す

        Args:
            musicname(str): 曲名
            playmode(str): プレイモード(SP or DP)
            difficulty(str): 難易度
            timestamp(str): タイムスタンプ
        '''
        musicname = event.get_string_at(0)
        playmode = event.get_string_at(1)
        difficulty = event.get_string_at(2)

        notebook = self.notebooks.get_notebook(musicname)
        if notebook is None:
            event.return_string(dumps(None))
            return

        event.return_string(dumps(notebook.get_scoreresult(playmode, difficulty)))

    def get_playresult(self, event: webui.Event):
        '''対象のリザルトの記録を返す
        '''
        musicname = event.get_string_at(0)
        playmode = event.get_string_at(1)
        difficulty = event.get_string_at(2)
        timestamp = event.get_string_at(3)

        notebook = self.notebooks.get_notebook(musicname)
        if notebook is None:
            event.return_string(dumps(None))
            return
        
        scoreresult = notebook.get_scoreresult(playmode, difficulty)
        if scoreresult is None:
            event.return_string(dumps(None))
            return
        
        if not 'history' in scoreresult or not timestamp in scoreresult['history']:
            event.return_string(dumps(None))
            return

        event.return_string(dumps(scoreresult['history'][timestamp]))
    
    def recents_save_resultimages(self, event: webui.Event):
        '''対象のリザルトの画像を保存する

        Args:
            timestams(list[str]): 対象のリザルトのタイムスタンプのリスト
        '''
        timestamps: list[str] = loads(event.get_string_at(0))

        if len(timestamps) == 0:
            return
        
        for timestamp in timestamps:
            if timestamp in results_today.keys() and not timestamp in timestamps_saved:
                save_result(results_today[timestamp], images_result[timestamp])
                notebook_recent.get_result(timestamp)['saved'] = True
                for result in recentresults:
                    if result.timestamp == timestamp:
                        result.saved = True
        
        notebook_recent.save()

        self.send_message('update_recentrecords', False)

    def recents_save_resultimages_filtered(self, event: webui.Event):
        '''対象のリザルトの画像をライバル欄にぼかしを入れて保存する

        選択しているすべてのリザルトにぼかし処理を実行する。
        ただし今日のリザルトでない場合は、リザルト画像がファイル保存されている場合のみ、処理が可能。

        Args:
            timestams(list[str]): 対象のリザルトのタイムスタンプのリスト
        '''
        timestamps: list[str] = loads(event.get_string_at(0))

        if len(timestamps) == 0:
            return
        
        updated = False
        new_filtereds = []
        for timestamp in timestamps:
            target = notebook_recent.get_result(timestamp)

            if not timestamp in images_result.keys():
                load_resultimages(timestamp, target['music'], target['play_mode'], target['difficulty'], True)

            if images_result[timestamp] is not None:
                if not timestamp in images_filtered.keys():
                    images_filtered[timestamp] = filter_result(
                        images_result[timestamp],
                        target['play_side'],
                        target['has_loveletter'],
                        target['has_graphtargetname'],
                        setting.filter_compact,
                    )
                if images_filtered[timestamp] is not None and not timestamp in timestamps_filteredsaved:
                    save_filtered(
                        images_filtered[timestamp],
                        timestamp,
                        target['music'],
                        target['play_mode'],
                        target['difficulty'],
                    )
                    target['filtered'] = True

                    new_filtereds.append(timestamp)

                    updated = True

        if updated:
            notebook_recent.save()

            for result in recentresults:
                if result.timestamp in new_filtereds:
                    result.filtered = True
            
            self.send_message('update_recentrecords', False)

    def recents_post_results(self, event: webui.Event):
        timestamps: list[str] = loads(event.get_string_at(0))

        if len(timestamps) == 0:
            return
        
        results = [notebook_recent.get_result(timestamp) for timestamp in timestamps]

        twitter.post_results(reversed(results), setting.hashtags)
    
    def recents_upload_collectionimages(self, event: webui.Event):
        timestamps: list[str] = loads(event.get_string_at(0))

        if len(timestamps) == 0:
            return

        for timestamp in timestamps:
            if timestamp in results_today.keys() and not timestamp in timestamps_uploaded:
                uploaded_informations, uploaded_details = storage.start_uploadcollection(results_today[timestamp], images_result[timestamp], True)
                if uploaded_informations and uploaded_details:
                    timestamps_uploaded.append(timestamp)
                if uploaded_informations:
                    api.send_message('append_log', f'upload informations collection: {timestamp}')
                if uploaded_details:
                    api.send_message('append_log', f'upload details collection: {timestamp}')

    def delete_musicresult(self, event: webui.Event):
        '''指定した曲の記録データを全て削除する
        
        Args:
            musicname(str): 対象の曲名
        '''
        musicname = event.get_string_at(0)

        notebooks_music.delete_notebook(musicname)

    def delete_scoreresult(self, event: webui.Event):
        '''指定した譜面の記録データを全て削除する
        
        Args:
            playmode(str): プレイモード(SP or DP)
            musicname(str): 対象の曲名
            difficulty(str): 譜面難易度
        '''
        playmode = event.get_string_at(0)
        musicname = event.get_string_at(1)
        difficulty = event.get_string_at(2)

        notebooks_music.get_notebook(musicname).delete_scoreresult(playmode, difficulty)
        # 統計やノーツレーダーの再計算
        # 譜面記録を再表示する
    
    def delete_playresult(self, event: webui.Event):
        '''指定したタイムスタンプの記録を削除する
        
        Args:
            playmode(str): プレイモード(SP or DP)
            musicname(str): 曲名
            difficulty(str): 譜面難易度
            timestamp(str): 選択したタイムスタンプ
        '''
        playmode = event.get_string_at(0)
        musicname = event.get_string_at(1)
        difficulty = event.get_string_at(2)
        timestamp = event.get_string_at(3)

        notebooks_music.get_notebook(musicname).delete_playresult(
            playmode,
            difficulty,
            timestamp,
        )

        # 統計やノーツレーダーの再計算
        # 譜面記録を再表示する
    
    def execute_findnewestversionaction(self, event: webui.Event):
        '''最新バージョンを見つけたときの処理を実行する
        
        実行と同時にリザルト手帳は終了する。
        '''
        self.findnewestversionaction()

    def output_csv(self, event: webui.Event):
        output(notebook_summary)
        output_notesradarcsv(notesradar)

    def clear_recent(self, event: webui.Event):
        recent.clear()
    
    def send_message(self, message: str, data:object = None):
        if data is None:
            newwindow.run(f'communication_message("{message}");')
        else:
            newwindow.run(f'communication_message("{message}", {dumps(data)});')
    
class GuiApiExport():
    '''エクスポート画面のAPIクラス
    '''
    window: webui.Window
    csssetting: dict = None

    @staticmethod
    def get_exportdirpath(event: webui.Event):
        '''エクスポートフォルダのパスの取得
        '''
        event.return_string(abspath(export_dirname))

    def __init__(self, window: webui.Window):
        self.window = window

        if not isfile(csssetting_filepath):
            return None
        
        with open(csssetting_filepath) as f:
            self.csssetting = load(f)

        window.bind('get_exportdirpath', GuiApiExport.get_exportdirpath)

        window.bind('get_csssetting', self.get_csssetting)
        window.bind('update_csssetting', self.update_csssetting)
        window.bind('save_csssetting', self.save_csssetting)

    def get_csssetting(self, event: webui.Event):
        '''CSS設定値の取得
        '''
        event.return_string(dumps(self.csssetting))
    
    def update_csssetting(self, event: webui.Event):
        csssetting = loads(event.get_string_at(0))

        self.csssetting = csssetting
    
    def save_csssetting(self, event: webui.Event):
        if self.csssetting is None:
            return

        with open(csssetting_filepath, 'w') as f:
            dump(self.csssetting, f, indent=2)

class GuiApiDiscordWebhook():
    events: dict = {}

    def __init__(self, window: webui.Window):
        self.window = window

        window.bind('discordwebhook_getpublics', self.get_publics)
        window.bind('discordwebhook_getnewpublics', self.get_newpublics)
        window.bind('discordwebhook_getjoineds', self.get_joineds)
        window.bind('discordwebhook_savesetting', self.save_setting)
        window.bind('discordwebhook_joinevent', self.join_event)
        window.bind('discordwebhook_leaveevent', self.leave_event)
        window.bind('discordwebhook_testpost', self.testpost)
        window.bind('discordwebhook_register', self.register)

    def get_publics(self, event: webui.Event):
        self.events = storage.download_discordwebhooks()

        if self.events is None:
            event.return_string(dumps(None))
            return
            
        publics = {}
        for key, value in self.events.items():
            if not value['private']:
                publics[key] = value
        
        event.return_string(dumps(publics))

    def get_newpublics(self, event: webui.Event):
        self.events = storage.download_discordwebhooks()
        newpublics = {}

        if self.events is not None:
            setting.discord_webhook['seenevents'] = [item for item in setting.discord_webhook['seenevents'] if item in self.events.keys()]
            for key, value in self.events.items():
                if not value['private'] and not key in setting.discord_webhook['seenevents']:
                    newpublics[key] = value
                    setting.discord_webhook['seenevents'].append(key)
        
        event.return_string(dumps(newpublics))

        setting.save()

    def get_joineds(self, event: webui.Event):
        event.return_string(dumps(setting.discord_webhook['joinedevents']))

    def save_setting(self, event: webui.Event):
        discordwebhooksetting = loads(event.get_string_at(0))

        setting.discord_webhook['playername'] = discordwebhooksetting['playername']
        setting.discord_webhook['filter'] = discordwebhooksetting['filter']

        setting.save()

    def join_event(self, event: webui.Event):
        '''
        イベントに参加する

        指定されたIDがない場合はFalseを返す。
        '''
        id = event.get_string_at(0)

        if not id in self.events.keys():
            event.return_string(dumps(False))
            return
        
        target = self.events[id]

        setting.discord_webhook['joinedevents'][id] = {
            'name': target['name'],
            'url': target['url'],
            'mode': target['mode'],
            'startdatetime': target['startdatetime'],
            'enddatetime': target['enddatetime'],
            'targetscore': target['targetscore'],
            'mybest': None,
        }

        setting.save()
        api.send_message('discordwebhook_refresh')

        event.return_string(dumps(True))

    def leave_event(self, event: webui.Event):
        id = event.get_string_at(0)

        del setting.discord_webhook['joinedevents'][id]

        setting.save()
        api.send_message('discordwebhook_refresh')

    def testpost(self, event: webui.Event):
        values = loads(event.get_string_at(0))

        ret = post_test(values['url'], values)

        event.return_string(dumps(ret))
    
    def register(self, event: webui.Event):
        values = loads(event.get_string_at(0))

        try:
            targetscore = None
            if values['mode'] != 'battle':
                targetscore = {
                    'musicname': values['targetscore']['musicname'],
                    'playmode': values['targetscore']['playmode'],
                    'difficulty': values['targetscore']['difficulty'],
                }
            
            discordwebhook = {
                'name': values['name'],
                'private': values['private'],
                'url': values['url'],
                'mode': values['mode'],
                'startdatetime': values['startdatetime'],
                'enddatetime': values['enddatetime'],
                'targetscore': targetscore,
            }

            id = str(uuid1())
            if(storage.upload_discordwebhook(f'{id}.json', discordwebhook)):
                event.return_string(dumps(id))
                ret = post_registered(values['url'], id)
            else:
                event.return_string(dumps(None))
        except Exception as ex:
            event.return_string(dumps(None))

class ScoreSelection():
    '''選択中の譜面

    曲名・プレイモード・譜面難易度を持つ。
    '''
    def __init__(self, musicname: str, playmode: str, difficulty: str):
        '''
        Args:
            musicname(str): 曲名
            playmode(str): プレイモード(SP or DP)
            difficulty(str): 譜面難易度
        '''
        self.musicname = musicname
        self.playmode = playmode
        self.difficulty = difficulty

def mainloop():
    while not event_close.wait(timeout=1):
        if not newwindow.is_shown():
            return
        if not queue_result_screen.empty():
            result_process(queue_result_screen.get_nowait())
        if not queue_musicselect_screen.empty():
            musicselect_process(queue_musicselect_screen.get_nowait())
        if not queue_messages.empty():
            queuemessage = queue_messages.get_nowait()
            if queuemessage == 'hotkey_start':
                start_hotkeys()
            if queuemessage == 'hotkey_stop':
                stop_hotkeys()
            if queuemessage in ['detect_loading', 'escape_loading']:
                api.send_message(queuemessage)
        if not queue_callfunction.empty():
            queue_callfunction.get_nowait()()
        if not queue_log.empty():
            api.send_message('append_log', queue_log.get_nowait())

def result_process(screen: Screen):
    '''リザルトを記録するときの処理をする

    Args:
        screen (Screen): screen.py
    '''
    global scoreselection

    api.send_message('append_log', 'result process')

    result: Result = recog.get_result(screen)
    if result is None:
        return

    if setting.play_sound:
        play_sound_result()
    
    resultimage = screen.original

    images_result[result.timestamp] = resultimage

    musicname = result.informations.music
    playmode = result.informations.play_mode
    difficulty = result.informations.difficulty

    if setting.display_result:
        if(musicname is not None and playmode is not None and difficulty is not None):
            scoreselection = ScoreSelection(musicname, playmode, difficulty)
        else:
            scoreselection = None

    if setting.data_collection or force_upload_enable:
        uploaded_informations, uploaded_details = storage.start_uploadcollection(result, resultimage, force_upload_enable)
        if uploaded_informations and uploaded_details:
            timestamps_uploaded.append(result.timestamp)
        if uploaded_informations:
            api.send_message('append_log', f'upload informations collection: {result.timestamp}')
        if uploaded_details:
            api.send_message('append_log', f'upload details collection: {result.timestamp}')

    filteredimage = None
    filteredimage_whole = None
    filteredimage_compact = None
    if setting.autosave_filtered:
        if not setting.filter_compact:
            filteredimage_whole = filter_result(
                resultimage,
                result.play_side,
                result.rival,
                result.details.graphtarget == 'rival',
                False,
            )
            filteredimage = filteredimage_whole
            images_filtered[result.timestamp] = filteredimage_whole
        else:
            filteredimage_compact = filter_result(
                resultimage,
                result.play_side,
                result.rival,
                result.details.graphtarget == 'rival',
                True,
            )
            filteredimage = filteredimage_compact
            images_filtered[result.timestamp] = filteredimage_compact

    if 'playername' in setting.discord_webhook.keys() and setting.discord_webhook['playername'] is not None and len(setting.discord_webhook['playername']) > 0:
        if 'joinedevents' in setting.discord_webhook.keys() and len(setting.discord_webhook['joinedevents']) > 0:
            imagevalue_discordwebhook = None
            if setting.discord_webhook['filter'] == discordwebhook_filtereds.NONE:
                imagevalue_discordwebhook = get_imagevalue(resultimage)
                imagevalues_result[result.timestamp] = imagevalue_discordwebhook
            if setting.discord_webhook['filter'] == discordwebhook_filtereds.WHOLE:
                if filteredimage_whole is None:
                    filteredimage_whole = filter_result(
                        resultimage,
                        result.play_side,
                        result.rival,
                        result.details.graphtarget == 'rival',
                        False,
                    )
                filteredimagevalue_whole = get_imagevalue(filteredimage_whole)
                if not setting.filter_compact:
                    imagevalues_filtered[result.timestamp] = filteredimagevalue_whole
                imagevalue_discordwebhook = filteredimagevalue_whole
            if setting.discord_webhook['filter'] == discordwebhook_filtereds.COMPACT:
                if filteredimage_compact is None:
                    filteredimage_compact = filter_result(
                        resultimage,
                        result.play_side,
                        result.rival,
                        result.details.graphtarget == 'rival',
                        True,
                    )
                filteredimagevalue_compact = get_imagevalue(filteredimage_compact)
                if setting.filter_compact:
                    imagevalues_filtered[result.timestamp] = filteredimagevalue_compact
                imagevalue_discordwebhook = filteredimagevalue_compact
            
            Thread(target=post_discord_webhooks, args=(result, imagevalue_discordwebhook)).start()
    
    if setting.newrecord_only and not result.has_new_record():
        return
    
    saved = False
    if setting.autosave:
        save_result(result, resultimage)
        saved = True
    
    filtered = False
    if setting.autosave_filtered:
        save_filtered(
            filteredimage,
            result.timestamp,
            result.informations.music,
            result.informations.play_mode,
            result.informations.difficulty,
        )
        filtered = True
    
    notebook_recent.append(result, saved, filtered)
    notebook_recent.save()

    if not result.dead or result.has_new_record():
        recent.insert(result)

    insert_results(result)

    if musicname is not None:
        notebook = notebooks_music.get_notebook(musicname)

        notebook.insert(result)
        notebook_summary.import_targetmusic(musicname, notebook)
        notebook_summary.save()

        if result.has_new_record():
            api.send_message('update_summary')

            if result.details.score.new:
                if notesradar.insert(
                    playmode,
                    musicname,
                    difficulty,
                    result.details.score.current,
                    notebook_summary.json['musics']
                ):
                    api.send_message('update_notesradar')

def musicselect_process(np_value):
    '''選曲画面で譜面を認識したときの処理をする

    Args:
        np_value (Screen): スクリーンショット画像データ
    '''
    global scoreselection

    api.send_message('append_log', 'musicselect process')

    playmode = recog.MusicSelect.get_playmode(np_value)
    if playmode is None:
        return
    
    difficulty = recog.MusicSelect.get_difficulty(np_value)
    if difficulty is None:
        return
    
    musicname = recog.MusicSelect.get_musicname(np_value)
    if musicname is None or not musicname in resource.musictable['musics'].keys():
        return
    
    if scoreselection is not None:
        if scoreselection.musicname == musicname and scoreselection.playmode == playmode and scoreselection.difficulty == difficulty:
            return
    
    scoreselection = ScoreSelection(musicname, playmode, difficulty)

    api.send_message('append_log', f'musicselect: {playmode}, {musicname}, {difficulty}')

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
    
    notebook = notebooks_music.get_notebook(musicname)
    
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
        api.send_message('update_summary')

        if notesradar.insert(
                playmode,
                musicname,
                difficulty,
                score,
                notebook_summary.json['musics']
            ):
            api.send_message('update_notesradar')
    
    api.send_message('scoreselect', {'playmode': playmode, 'musicname': musicname, 'difficulty': difficulty})

def post_discord_webhooks(result: Result, imagevalue: bytes):
    setting_updated = False
    posttargets = []
    deletetargets = []
    logs = []

    for key, webhooksetting in setting.discord_webhook['joinedevents'].items():
        nowdt = datetime.now(timezone.utc)
        startdt = datetime.strptime(webhooksetting['startdatetime'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        enddt = datetime.strptime(webhooksetting['enddatetime'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        
        if nowdt > enddt:
            deletetargets.append(key)
            continue

        if nowdt >= startdt:
            posttargets.append(webhooksetting)

    if len(deletetargets):
        setting_updated = True
        for key in deletetargets:
            del setting.discord_webhook['joinedevents'][key]

    if len(posttargets):
        dt = datetime.now().strftime('%H:%M')
        
        for webhooksetting in posttargets:
            postresult, resultmessages = post_result(setting.discord_webhook['playername'], webhooksetting, result, imagevalue)
            if postresult is None:
                continue

            settingname = webhooksetting['name']

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
                if type(resultmessages) == str:
                    logs.append(f'{dt} {settingname}: {resultmessages}')
                else:
                    logs.append(f'{dt} {settingname}: {resultmessages[0]}')
                    for line in resultmessages[1:]:
                        logs.append(line)
    
    if setting_updated:
        setting.save()
        api.send_message('discordwebhook_refresh')
    
    api.send_message('discordwebhook_append_log', logs)

def save_result(result: Result, image: Image.Image):
    if result.timestamp in timestamps_saved:
        return
    
    ret = None
    try:
        music = result.informations.music
        scoretype = {'playmode': result.informations.play_mode, 'difficulty': result.informations.difficulty}
        ret = save_resultimage(image, music, result.timestamp, setting.imagesave_path, scoretype, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        api.send_message('error', ['リザルト画像の保存に失敗しました。'])
        return

    if ret:
        timestamps_saved.append(result.timestamp)

def save_filtered(filteredimage: Image.Image, timestamp: str, music: str, play_mode: str, difficulty: str):
    '''リザルト画像にぼかしを入れて保存する

    Args:
        filteredimage (Image): 対象の画像(PIL)
        timestamp (str): リザルトのタイムスタンプ
        music (str): 曲名
        play_mode (str): プレイモード
        difficulty (str): 譜面難易度

    Returns:
        Image: ぼかしを入れた画像
    '''
    if timestamp in timestamps_filteredsaved:
        return
    
    ret = None
    try:
        scoretype = {'playmode': play_mode, 'difficulty': difficulty}
        ret = save_resultimage_filtered(filteredimage, music, timestamp, setting.imagesave_path, scoretype, setting.savefilemusicname_right)
    except Exception as ex:
        logger.exception(ex)
        api.send_message('error', ['リザルト画像の保存に失敗しました。'])
        return

    if ret:
        images_filtered[timestamp] = filteredimage
        timestamps_filteredsaved.append(timestamp)

def insert_recentnotebook_results():
    for timestamp in notebook_recent.timestamps:
        target = notebook_recent.get_result(timestamp)
        if target is None:
            continue
        
        newresult = RecentResult(timestamp)

        newresult.musicname = target['music']
        newresult.playmode = target['play_mode']
        newresult.difficulty = target['difficulty']
        newresult.news.cleartype = target['clear_type_new']
        newresult.news.djlevel = target['dj_level_new']
        newresult.news.score = target['score_new']
        newresult.news.misscount = target['miss_count_new']
        newresult.saved = target['saved']
        newresult.filtered = target['filtered']

        recentresults.insert(0, newresult)

def insert_results(result: Result):
    results_today[result.timestamp] = result

    newresult = RecentResult(result.timestamp)

    newresult.musicname = result.informations.music
    newresult.playmode = result.informations.play_mode
    newresult.difficulty = result.informations.difficulty
    newresult.news.cleartype = result.details.clear_type.new
    newresult.news.djlevel = result.details.dj_level.new
    newresult.news.score = result.details.score.new
    newresult.news.misscount = result.details.miss_count.new
    newresult.latest = True
    newresult.saved = result.timestamp in timestamps_saved
    newresult.filtered = result.timestamp in images_filtered.keys()

    recentresults.insert(0, newresult)

    while len(recentresults) > recent_maxcount:
        del recentresults[-1]

    api.send_message('update_recentrecords', setting.display_result)

def update_resultflag(row_index, saved=False, filtered=False):
    if saved:
        recentresults[row_index].saved = True
    if filtered:
        recentresults[row_index].filtered = True

def active_screenshot():
    if not screenshot.shot():
        return
    
    if setting.play_sound:
        play_sound_result()

    image = screenshot.get_image()
    if image is None:
        return
    
    timestamp, filepath = save_raw(image)
    api.send_message('append_log', f'save screen: {filepath}')

    api.image_activescreenshot = get_imagevalue(image)

    api.send_message('activescreenshot', filepath)

    socket_server.update_screenshot(get_imagevalue(image))

def select_summary():
    api.send_message('switch_displaytab', {'groupname': 'main', 'tabname': 'summary'})

def select_notesradar():
    api.send_message('switch_displaytab', {'groupname': 'main', 'tabname': 'notesradar'})

def select_screenshot():
    api.send_message('switch_displaytab', {'groupname': 'main', 'tabname': 'screenshot'})

def select_scoreinformation():
    api.send_message('switch_displaytab', {'groupname': 'main', 'tabname': 'scoreinformation'})

def select_scoregraph():
    api.send_message('switch_displaytab', {'groupname': 'main', 'tabname': 'chartscoreresult'})

def upload_musicselect():
    '''
    選曲画面の一部を学習用にアップロードする
    '''
    if not screenshot.shot():
        return
    
    if setting.play_sound:
        play_sound_result()

    image = screenshot.get_image()
    if image is None:
        return
    
    storage.start_uploadmusicselect(image)

    api.send_message('append_log', f'upload screen')

    api.image_activescreenshot = get_imagevalue(image)

    api.send_message('musicselect_upload')

    socket_server.update_screenshot(get_imagevalue(image))

def check_latest_version():
    if version == '0.0.0.0':
        return None, None
    
    latest_version = get_latest_version()

    if latest_version == version:
        return None, None
    
    dev = 'dev' in version
    if dev:
        v = version.split('dev')[0]
    else:
        v = version

    splitted_version = [*map(int, v.split('.'))]
    splitted_latest_version = [*map(int, latest_version.split('.'))]
    for i in range(len(splitted_latest_version)):
        if splitted_version[i] > splitted_latest_version[i]:
            return None, None
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
            return None, None
        if splitted_version[i] < splitted_latest_version[i]:
            break

    action = None
    config = LocalConfig()
    if config.installer_filepath is not None:
        if config.installer_filepath.exists():
            def action():
                Popen(config.installer_filepath)
                newwindow.close()
            message = find_latest_version_message_has_installer
    
    if action is None:
        def action():
            webbrowser.open(wiki_url)
        message = find_latest_version_message_not_has_installer
    
    return message, action

def get_latest_version():
    with request.urlopen(latest_url) as response:
        response: HTTPResponse
        url = response.geturl()
        version = url.split('/')[-1]
        api.send_message('append_log', f'released latest version: {version}')
        if version[0] == 'v':
            return version.removeprefix('v')
        else:
            return None

def initial_records_processing():
    '''起動時一回だけの記録ファイルの処理
    - 長い曲名のファイル名の修正
    - 曲名の変更に伴う記録ファイルのファイル名変更
    '''
    if resource.musictable is not None:
        rename_allfiles(resource.musictable['musics'].keys())

    changed = rename_changemusicname()

    api.send_message('start_summaryprocessing')

    if not 'last_allimported' in notebook_summary.json.keys():
        notebook_summary.import_allmusics(version)
        notebook_summary.save()
    else:
        if len(changed) > 0:
            for musicname, renamed in changed:
                del notebook_summary.json['musics'][musicname]
                notebook = notebooks_music.get_notebook(renamed)
                notebook_summary.import_targetmusic(renamed, notebook)

            notebook_summary.save()

def check_resource():
    '''リソースファイルの確認

    GCPにアクセスしてリソースファイルの最新状態を確認する。
    最新ファイルがある場合はダウンロードする。
    '''
    api.send_message('start_resourcecheck')

    informations_filename = f'{define.informations_resourcename}.res'
    if check_latest(storage, informations_filename):
        resource.load_resource_informations()

    details_filename = f'{define.details_resourcename}.res'
    if check_latest(storage, details_filename):
        resource.load_resource_details()

    musictable_filename = f'{define.musictable_resourcename}.res'
    if check_latest(storage, musictable_filename):
        resource.load_resource_musictable()

    musicselect_filename = f'{define.musicselect_resourcename}.res'
    if check_latest(storage, musicselect_filename):
        resource.load_resource_musicselect()

    notesradar_filename = f'{define.notesradar_resourcename}.res'
    if check_latest(storage, notesradar_filename):
        resource.load_resource_notesradar()

    check_latest(storage, musicnamechanges_filename)

    api.send_message('append_log', 'complete check resources')

def load_resultimages(playmode: str, musicname: str, difficulty: str, timestamp: str, recent=False):
    '''リザルト画像をファイルからロードする
    
    対象のリザルトが起動中に記録したリザルトでない場合は実行する。
    Args:
        timestamp(str): 対象のリザルトのタイムスタンプ
        music(str): 曲名
        playmode(str): プレイモード(SP or DP)
        difficulty(str): 譜面難易度
        recent(bool): 最近のプレイにある
    '''
    if len(playmode) == 0:
        playmode = None
    if len(musicname) == 0:
        musicname = None
    if len(difficulty) == 0:
        difficulty = None
    
    scoretype = {'playmode': playmode, 'difficulty': difficulty}

    image_result = get_resultimage(musicname, timestamp, setting.imagesave_path, scoretype)
    images_result[timestamp] = image_result
    if image_result is not None:
        timestamps_saved.append(timestamp)

    image_filtered = get_resultimage_filtered(musicname, timestamp, setting.imagesave_path, scoretype)
    if not recent or image_result is None or image_filtered is not None:
        images_filtered[timestamp] = image_filtered

def start_hotkeys():
    if setting.hotkeys is None:
        return
    
    if 'active_screenshot' in setting.hotkeys.keys() and setting.hotkeys['active_screenshot'] != '':
        keyboard.add_hotkey(setting.hotkeys['active_screenshot'], active_screenshot)
    if 'select_summary' in setting.hotkeys.keys() and setting.hotkeys['select_summary'] != '':
        keyboard.add_hotkey(setting.hotkeys['select_summary'], select_summary)
    if 'select_notesradar' in setting.hotkeys.keys() and setting.hotkeys['select_notesradar'] != '':
        keyboard.add_hotkey(setting.hotkeys['select_notesradar'], select_notesradar)
    if 'select_screenshot' in setting.hotkeys.keys() and setting.hotkeys['select_screenshot'] != '':
        keyboard.add_hotkey(setting.hotkeys['select_screenshot'], select_screenshot)
    if 'select_scoreinformation' in setting.hotkeys.keys() and setting.hotkeys['select_scoreinformation'] != '':
        keyboard.add_hotkey(setting.hotkeys['select_scoreinformation'], select_scoreinformation)
    if 'select_scoregraph' in setting.hotkeys.keys() and setting.hotkeys['select_scoregraph'] != '':
        keyboard.add_hotkey(setting.hotkeys['select_scoregraph'], select_scoregraph)
    if 'upload_musicselect' in setting.hotkeys.keys() and setting.hotkeys['upload_musicselect'] != '':
        keyboard.add_hotkey(setting.hotkeys['upload_musicselect'], upload_musicselect)

def stop_hotkeys():
    for target in [active_screenshot, upload_musicselect, select_summary, select_notesradar, select_screenshot, select_scoreinformation, select_scoregraph]:
        try:
            keyboard.remove_hotkey(target)
        except Exception as ex:
            api.send_message('append_log', '\n'.join(('failed stop hotkey.', str(ex))))

if __name__ == '__main__':
    if gethandle(windowtitle) is not None:
        show_messagebox('多重起動はできません。', windowtitle)
        exit()
    
    generate_exportsettingcss(setting.port['socket'])

    detect_infinitas: bool = False
    capture_enable: bool = False

    force_upload_enable: bool = False

    screenshot = Screenshot()

    notebook_recent = NotebookRecent(recent_maxcount)
    notebook_summary = NotebookSummary()
    notebooks_music = Notebooks()

    notesradar = NotesRadar()

    results_today = {}
    timestamps_saved = []
    timestamps_filteredsaved = []
    timestamps_uploaded = []

    images_result = {}
    images_filtered = {}
    imagevalues_result = {}
    imagevalues_filtered = {}

    scoreselection: ScoreSelection = None

    recent = Recent()

    recentresults: list[RecentResult] = []

    queue_log = Queue()
    queue_result_screen = Queue(1)
    queue_musicselect_screen = Queue(1)
    queue_messages = Queue()
    queue_multimessages = Queue()
    queue_callfunction = Queue()

    storage = StorageAccessor()

    event_close = Event()
    thread = ThreadMain(
        event_close,
        queues = {
            'log': queue_log,
            'result_screen': queue_result_screen,
            'musicselect_screen': queue_musicselect_screen,
            'messages': queue_messages,
            'multimessages': queue_multimessages
        }
    )

    insert_recentnotebook_results()

    socket_server = SocketServer(port=setting.port['socket'])
    socket_server.start()

    webui.set_config(webui.Config.multi_client, True)
    webui.set_default_root_folder('web/')

    newwindow = webui.Window()
    newwindow.set_size(1000, 600)
    newwindow.set_port(setting.port['main'])
    newwindow.set_public(True)


    api = GuiApi(newwindow, notebooks_music)
    api_export = GuiApiExport(newwindow)
    api_discordwebhook = GuiApiDiscordWebhook(newwindow)

    newwindow.show('index.html')
    handle = gethandle(windowtitle)
    if handle is None:
        show_messagebox('起動に失敗しました。', windowtitle)
        exit()
    
    change_window_setting(handle)

    mainloop()

    webui.clean()

    socket_server.stop()
    event_close.set()

    socket_server.join()
    thread.join()

    del screenshot
    
    output(notebook_summary)
    output_notesradarcsv(notesradar)
