import json
from os import getcwd

from define import Playmodes

setting_filepath = 'setting.json'

default = {
    'newrecord_only': False,
    'play_sound': False,
    'autosave': False,
    'autosave_filtered': False,
    'filter_compact': False,
    'filter_overlay': {
        'use': False,
        'rival': {
            'imagefilepath': None,
            'offset': (0, 0, ),
            'scalefactor': 1,
        },
        'loveletter': {
            'imagefilepath': None,
            'offset': (0, 0, ),
            'scalefactor': 1,
        },
        'rivalname': {
            'imagefilepath': None,
            'offset': (0, 0, ),
            'scalefactor': 1,
        },
    },
    'savefilemusicname_right': False,
    'hotkeys': {
        'active_screenshot': 'alt+F10',
        'select_summary': 'alt+U',
        'select_notesradar': 'alt+R',
        'select_screenshot': 'alt+T',
        'select_scoreinformation': 'alt+I',
        'select_scoregraph': 'alt+G',
        'upload_musicselect': 'alt+F8',
    },
    'summary_countmethod_only': False,
    'display_result': False,
    'resultimage_filtered': False,
    'imagesave_path': getcwd(),
    'startup_image': 'notesradar',
    'hashtags': '#IIDX #infinitas573 #infnotebook',
    'data_collection': False,
    'summaries' : {
        Playmodes.SP: {
            '8': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '9': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '10': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '11': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '12': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
        },
        Playmodes.DP: {
            '8': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '9': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '10': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '11': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
            '12': {'cleartypes': ['F-COMBO'], 'djlevels': ['AAA']},
        },
    },
    'discord_webhook': {
        'playername': 'NO NAME',
        'seenevents': [],
        'joinedevents': {},
    },
    'port': {
        'main': 52374,
        'socket': 57328,
    },
}

class Setting():
    def __init__(self):
        try:
            with open(setting_filepath) as f:
                self.json = json.load(f)
        except Exception:
            self.json = default

        for k in default.keys():
            if not k in self.json.keys():
                self.json[k] = default[k]
        
        # バージョンアップによる仕様変更の対処
        if 'display_saved_result' in self.json.keys():
            self.json['display_result'] = self.json['display_saved_result']
            del self.json['display_saved_result']
        if 'save_newrecord_only' in self.json.keys():
            self.json['newrecord_only'] = self.json['save_newrecord_only']
            del self.json['save_newrecord_only']
        if 'autoexport' in self.json.keys():
            del self.json['autoexport']
        if 'manage' in self.json.keys():
            self.json['debug'] = self.json['manage']
            del self.json['manage']
        if 'display_music' in self.json.keys():
            del self.json['display_music']
        if 'djname' in self.json['discord_webhook'].keys():
            self.json['discord_webhook']['playername'] = self.json['discord_webhook']['djname']
            del self.json['discord_webhook']['djname']
        if 'servers' in self.json['discord_webhook'].keys():
            del self.json['discord_webhook']['servers']
        if not 'playername' in self.json['discord_webhook'].keys():
            self.json['discord_webhook']['playername'] = default['discord_webhook']['playername']
        if not 'seenevents' in self.json['discord_webhook'].keys():
            self.json['discord_webhook']['seenevents'] = []
        if not 'joinedevents' in self.json['discord_webhook'].keys():
            self.json['discord_webhook']['joinedevents'] = {}
        if not 'select_summary' in self.json['hotkeys'].keys():
            self.json['hotkeys']['select_summary'] = default['hotkeys']['select_summary']
        if not 'select_notesradar' in self.json['hotkeys'].keys():
            self.json['hotkeys']['select_notesradar'] = default['hotkeys']['select_notesradar']
        if not 'select_screenshot' in self.json['hotkeys'].keys():
            self.json['hotkeys']['select_screenshot'] = default['hotkeys']['select_screenshot']
        if not 'select_scoreinformation' in self.json['hotkeys'].keys():
            self.json['hotkeys']['select_scoreinformation'] = default['hotkeys']['select_scoreinformation']
        if not 'select_scoregraph' in self.json['hotkeys'].keys():
            self.json['hotkeys']['select_scoregraph'] = default['hotkeys']['select_scoregraph']
        if not 'filter_overlay' in self.json.keys():
            self.json['filter_overlay'] = default['filter_overlay']
        if not 'use' in self.json['filter_overlay'].keys():
            self.json['filter_overlay']['use'] = default['filter_overlay']['use']
        for key in ['rival', 'loveletter', 'rivalname']:
            if not key in self.json['filter_overlay'].keys():
                self.json['filter_overlay'][key] = default['filter_overlay'][key]
            if not 'imagefilepath' in self.json['filter_overlay'][key].keys():
                self.json['filter_overlay'][key]['imagefilepath'] = default['filter_overlay'][key]['imagefilepath']
            if not 'offset' in self.json['filter_overlay'][key].keys():
                self.json['filter_overlay'][key]['offset'] = default['filter_overlay'][key]['offset']
            if not 'scalefactor' in self.json['filter_overlay'][key].keys():
                self.json['filter_overlay'][key]['scalefactor'] = default['filter_overlay'][key]['scalefactor']

        self.save()

    def save(self):
        try:
            with open(setting_filepath, 'w') as f:
                json.dump(self.json, f, indent=2)
        except Exception as ex:
            print(f'setting json dump error: {ex}')
    
    def has_key(self, key):
        return key in self.json.keys()

    def get_value(self, key):
        if not key in self.json.keys():
            return False
        
        return self.json[key]

    def set_value(self, key, value):
        self.json[key] = value

    @property
    def newrecord_only(self):
        '''更新があったときのみ記録する
        '''
        return self.get_value('newrecord_only')

    @newrecord_only.setter
    def newrecord_only(self, value: bool):
        self.set_value('newrecord_only', value)
    
    @property
    def play_sound(self):
        '''リザルトを認識した時等に音を鳴らす
        '''
        return self.get_value('play_sound')

    @play_sound.setter
    def play_sound(self, value: bool):
        self.set_value('play_sound', value)
    
    @property
    def autosave(self):
        '''リザルト画像を自動保存する
        '''
        return self.get_value('autosave')

    @autosave.setter
    def autosave(self, value: bool):
        self.set_value('autosave', value)
    
    @property
    def autosave_filtered(self):
        '''ライバルを隠したリザルト画像を自動保存する
        '''
        return self.get_value('autosave_filtered')

    @autosave_filtered.setter
    def autosave_filtered(self, value: bool):
        self.set_value('autosave_filtered', value)
    
    @property
    def filter_compact(self):
        '''ライバル隠しを最小にする
        '''
        return self.get_value('filter_compact')

    @filter_compact.setter
    def filter_compact(self, value: bool):
        self.set_value('filter_compact', value)
    
    @property
    def filter_overlay(self):
        '''ライバル隠しに重ねる画像の設定
        '''
        return self.get_value('filter_overlay')

    @filter_overlay.setter
    def filter_overlay(self, value: dict[str, any]):
        self.set_value('filter_overlay', value)
    
    @property
    def savefilemusicname_right(self):
        '''画像ファイルのファイル名につける曲名を最後にする
        '''
        return self.get_value('savefilemusicname_right')

    @savefilemusicname_right.setter
    def savefilemusicname_right(self, value: bool):
        self.set_value('savefilemusicname_right', value)
    
    @property
    def hotkeys(self):
        '''ショートカットキーの設定
        '''
        return self.get_value('hotkeys')

    @hotkeys.setter
    def hotkeys(self, value: dict[str, str]):
        self.set_value('hotkeys', value)
    
    @property
    def summary_countmethod_only(self):
        '''統計の譜面数のカウント方式が、該当するもののみ

        そうでない場合は、例えばEXH-CLEAR等もF-COMBOに含める。
        '''
        return self.get_value('summary_countmethod_only')

    @summary_countmethod_only.setter
    def summary_countmethod_only(self, value: bool):
        self.set_value('summary_countmethod_only', value)
    
    @property
    def display_result(self):
        '''リザルトを記録時にそのリザルトを選択する
        '''
        return self.get_value('display_result')

    @display_result.setter
    def display_result(self, value: bool):
        self.set_value('display_result', value)
    
    @property
    def resultimage_filtered(self):
        '''表示リザルト画像のフィルター
        '''
        return self.get_value('resultimage_filtered')

    @resultimage_filtered.setter
    def resultimage_filtered(self, value):
        self.set_value('resultimage_filtered', value)

    @property
    def imagesave_path(self):
        '''リザルト画像等のファイルの保存先のフォルダパス
        '''
        return self.get_value('imagesave_path')

    @imagesave_path.setter
    def imagesave_path(self, value: str):
        self.set_value('imagesave_path', value)
    
    @property
    def startup_image(self):
        '''リザルト手帳の初期処理完了後に選択状態にするタブの設定
        '''
        return self.get_value('startup_image')
    
    @startup_image.setter
    def startup_image(self, value: str):
        self.set_value('startup_image', value)
    
    @property
    def hashtags(self):
        '''ポストの本文に付与する文字列
        '''
        return self.get_value('hashtags')
    
    @hashtags.setter
    def hashtags(self, value: str):
        self.set_value('hashtags', value)
    
    @property
    def data_collection(self):
        '''収集画像をアップロードする
        '''
        return self.get_value('data_collection')

    @data_collection.setter
    def data_collection(self, value: bool):
        self.set_value('data_collection', value)
    
    @property
    def summaries(self):
        '''統計出力設定
        '''
        return self.get_value('summaries')

    @summaries.setter
    def summaries(self, value):
        self.set_value('summaries', value)
    
    @property
    def discord_webhook(self):
        '''イベント設定
        '''
        return self.get_value('discord_webhook')

    @discord_webhook.setter
    def discord_webhook(self, value):
        self.set_value('discord_webhook', value)

    @property
    def port(self):
        '''ポート設定
        '''
        return self.get_value('port')

    @port.setter
    def port(self, value):
        self.set_value('port', value)

    @property
    def ignore_download(self):
        '''最新リソースファイルの取得を無効にする
        '''
        return self.get_value('ignore_download')

    @property
    def debug(self):
        '''デバッグモード

        デバッグ用のログ表示を有効にする。
        '''
        return self.get_value('debug')
