from datetime import datetime
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from define import Playmodes,Playtypes,ResultTabs,NotesradarAttributes,define

results_dirname = 'results'
filtereds_dirname = 'filtered'

class ResultInformations():
    def __init__(self, playmode: str, difficulty: str, level: str, notes: int, playspeed: float | None, songname: str):
        self.playmode = playmode
        self.difficulty = difficulty
        self.level = level
        self.notes = notes
        self.playspeed = playspeed
        self.songname = songname

class ResultValues():
    def __init__(self, best: str | int, current: str | int, new: bool):
        self.best = best
        self.current = current
        self.new = new

class ResultOptions():
    arrange: str | None = None
    '''配置オプション'''

    flip: str | None = None
    '''DPオンリー 左右の譜面が入れ替わる'''

    assist: str | None = None
    '''A-SCR or LEGACY'''

    battle: bool | None = None
    '''DP時にBATTLEがON 両サイドがSP譜面になる'''

    allscratch: bool | None = None
    '''鍵盤がスクラッチにアサインされる'''

    regularspeed: bool | None = None
    '''曲のbpmに影響されずにノーツの速度が固定化される'''

    notrecord: bool | None = None
    '''記録しないリザルト 配置にH-RANを含む ALL-SCR REGUL-SPEED'''

    record_achievements: bool | None = None
    '''実績を記録する REGUL-SPEEDを使用しておらず、固定配置系かS-RANDAMかALL-SCRか'''

    def __init__(self, arrange: str, flip: str, assist: str, battle: bool, allscratch: bool, regularspeed: bool):
        self.arrange = arrange
        self.flip = flip
        self.assist = assist
        self.battle = battle
        self.allscratch = allscratch
        self.regularspeed = regularspeed

        self.notrecord = (arrange is not None and 'H-RAN' in arrange) or self.allscratch or self.regularspeed

        if (arrange is None or not 'H-RAN' in arrange) and not self.regularspeed:
            if not self.allscratch:
                if arrange in (None, 'MIRROR', 'OFF/MIR', 'MIR/OFF', 'MIR/MIR',):
                    self.record_achievements = True
                if arrange in ('S-RANDOM', 'S-RAN/S-RAN',):
                    self.record_achievements = True
            else:
                self.record_achievements = True

class ResultDetails():
    def __init__(self, graphtype: str, options: ResultOptions, clear_type: ResultValues, dj_level: ResultValues, score: ResultValues, miss_count: ResultValues, graphtarget: str):
        self.graphtype = graphtype
        self.options = options
        self.clear_type = clear_type
        self.dj_level = dj_level
        self.score = score
        self.miss_count = miss_count
        self.graphtarget = graphtarget

class ResultOthers():
    class ResultOthersRival():
        def __init__(self, rankbefore: int, ranknow: int, rankposition: int):
            self.rankbefore = rankbefore
            self.ranknow = ranknow
            self.rankposition = rankposition

    class ResultOthersNotesradar():
        def __init__(self, attribute: NotesradarAttributes, chartvalue: float, value: float):
            self.attribute = attribute
            self.chartvalue = chartvalue
            self.value = value

    def __init__(self, tab: ResultTabs, rival: ResultOthersRival, notesradar: ResultOthersNotesradar):
        self.tab = tab
        self.rival = rival
        self.notesradar = notesradar

class Result():
    has_new: bool | None = None
    '''NEWアイコンがある'''
    has_new_original: bool | None = None
    '''プレイ履歴と比較した結果更新がある'''
    originalnews: dict[str | bool] = None
    '''BATTLEやALL-SCRのときの更新状況'''

    others: ResultOthers | None = None

    def __init__(self, playside: str, has_loveletter: bool, is_dead: bool, informations: ResultInformations | None, details: ResultDetails | None):
        self.playside: str = playside
        self.has_loveletter: bool = has_loveletter
        self.is_dead: bool = is_dead

        self.informations: ResultInformations | None = informations
        self.details: ResultDetails | None = details

        self.set_playtype()

        self.check_new()

        now = datetime.now()
        self.timestamp = f'{now.strftime('%Y%m%d-%H%M%S')}'
    
    @property
    def has_newrecord(self):
        '''更新がある
        '''
        return self.has_new or self.has_new_original
    
    def set_playtype(self):
        '''プレイの種類をセットする
        
        DPでなおかつBATTLEの場合は'DP BATTLE'とする
        '''
        self.playtype = None

        if self.informations is None:
            return
        if self.informations.playmode is None:
            return
        if self.informations.difficulty is None:
            return
        
        if self.informations.playmode == Playmodes.SP:
            self.playtype = Playmodes.SP
            return
        
        if self.details is None:
            return
        if self.details.options is None:
            return
        
        if not self.details.options.battle:
            self.playtype = Playmodes.DP
        else:
            self.playtype = Playtypes.DPBATTLE
        
    def check_new(self):
        if self.details is None:
            return
        
        self.has_new = any([
            self.details.clear_type is not None and self.details.clear_type.new,
            self.details.dj_level is not None and self.details.dj_level.new,
            self.details.score is not None and self.details.score.new,
            self.details.miss_count is not None and self.details.miss_count.new,
        ])
    
    def battle_checknew(self, record: dict):
        if self.informations is None or self.details is None:
            return
        
        if self.informations.difficulty is None:
            return

        if self.informations.playspeed is not None:
            return
        
        if self.details.options is None:
            return
        
        if self.details.options.notrecord:
            return

        if not self.details.options.battle:
            return
        
        self.originalnews = {}

        update_all = False
        if not self.playtype in record.keys():
            update_all = True
        else:
            difficulty = self.informations.difficulty
        
            if record[self.playtype] is None or not difficulty in record[self.playtype].keys():
                update_all = True
            else:
                if record[self.playtype][difficulty] is None or not 'best' in record[self.playtype][difficulty].keys():
                    update_all = True
                else:
                    update_all = record[self.playtype][difficulty]['best'] is None

        if not update_all:
            bests = record[self.playtype][difficulty]['best']
        
        targets = {
            'clear_type': self.details.clear_type,
            'dj_level': self.details.dj_level,
            'score': self.details.score,
            'miss_count': self.details.miss_count,
        }

        for key, value in targets.items():
            if value.current is None:
                self.originalnews[key] = False
                continue

            update = update_all
            if not update:
                if not key in bests.keys() or bests[key]['value'] is None:
                    update = True
                else:
                    if key in ['clear_type', 'dj_level']:
                        if key == 'clear_type':
                            value_list = define.value_list['clear_types']
                        if key == 'dj_level':
                            value_list = define.value_list['dj_levels']
                        
                        nowbest_index = value_list.index(bests[key]['value'])
                        current_index = value_list.index(value.current)
                        if nowbest_index < current_index:
                            update = True
                    
                    if key in ['score', 'miss_count']:
                        if value.current > bests[key]['value']:
                            update = True

            self.originalnews[key] = update

            if update:
                self.has_new_original = True

class RecentResult():
    class NewFlags():
        cleartype: bool = False
        djlevel: bool = False
        score: bool = False
        misscount: bool = False
    
    timestamp: str
    musicname: str = None
    playtype: str = None
    difficulty: str = None
    news: NewFlags = None
    latest: bool = False
    saved: bool = False
    filtered: bool = False

    def __init__(self, timestamp: str):
        self.timestamp = timestamp
        self.news = self.NewFlags()
    
    def encode(self):
        return {
            'timestamp': self.timestamp,
            'musicname': self.musicname,
            'playtype': self.playtype,
            'difficulty': self.difficulty,
            'news_cleartype': self.news.cleartype,
            'news_djlevel': self.news.djlevel,
            'news_score': self.news.score,
            'news_misscount': self.news.misscount,
            'latest': self.latest,
            'saved': self.saved,
            'filtered': self.filtered,
        }
