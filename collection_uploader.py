from time import time
from decimal import Decimal,ROUND_UP
from logging import getLogger

logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from PIL import Image
from numpy import array

from define import Graphtypes,ResultTabs,define
from resources import resource
from result import Result,ResultInformations,ResultDetails
from setting import Setting
from storage import StorageAccessor
from recog import Recognition as recog

class CollectionUploader():
    class MusicSelectUnknownMusicNameChecker():
        '''選曲画面の曲名認識チェッカー
        '''
        time: float | None = None
        '''曲名の認識の不明を拾った時の時間'''
        processed: bool = False
        '''処理済み'''

        def reset(self):
            self.time = None
            self.processed = False
        
        def evaluate(self):
            if self.time is not None:
                if not self.processed and time() - self.time > 5.0:
                    self.processed = True
                    return True
            else:
                self.time = time()
            
            return False

    class ResultOthersNotesradarChecker():
        '''リザルトのノーツレーダー値のチェッカー
        '''
        playside: str = None
        '''プレイサイド'''
        informations: ResultInformations = None
        '''譜面情報'''
        details: ResultDetails = None
        '''詳細'''
        attributes: list[str] = []
        '''譜面のレーダー値'''

        def reset(self):
            self.playside = None
            self.informations = None
            self.details = None
            self.attributes = []
        
        def evaluate(self, npvalue:array) -> float:
            if self.playside is None:
                self.playside = recog.Result.get_play_side(npvalue)
            
            if self.playside is None:
                return None
            
            if self.informations is None:
                npvalue_informations = npvalue[define.areas_np['informations']]
                self.informations = recog.Result.get_informations(npvalue_informations)
            
            if self.informations is None:
                return None
            if self.informations.music is None:
                return None
            if self.informations.difficulty is None:
                return None
            if self.informations.notes is None:
                return None

            if self.details is None:
                npvalue_details = npvalue[define.areas_np['details'][self.playside]]
                self.details = recog.Result.get_details(npvalue_details)
            
            if self.details is None:
                return None
            if self.details.score.current is None:
                return None
            
            npvalue_others = npvalue[define.areas_np['resultothers'][self.playside]]
            if recog.ResultOthers.get_tab(npvalue_others) != ResultTabs.RADAR:
                return None
            
            attribute = recog.ResultOthers.get_notesradar_attribute(npvalue_others)
            if attribute is None or attribute in self.attributes:
                return None
            
            self.attributes.append(attribute)

            return (attribute, recog.ResultOthers.get_notesradar_chartvalue(npvalue_others),)
    
    musicselectchecker = MusicSelectUnknownMusicNameChecker()
    notesradarchecker = ResultOthersNotesradarChecker()

    def __init__(self, setting:Setting, storage:StorageAccessor):
        self.setting = setting
        self.storage = storage
    
    def checkandupload_result(self, result:Result, image:Image.Image, force:bool) -> bool:
        upload_informations = force or result.informations is None
        if not upload_informations:
            if result.informations.play_mode is None:
                upload_informations = True
            if result.informations.difficulty is None:
                upload_informations = True
            if result.informations.level is None:
                upload_informations = True
            if result.informations.music is None:
                upload_informations = True

        if upload_informations:
            self.storage.start_uploadinformations(image)
        
        upload_details = force or result.details is None
        if not upload_details:
            if result.details.clear_type is None or result.details.clear_type.current is None:
                upload_details = True
            if result.details.dj_level is None or result.details.dj_level.current is None:
                upload_details = True
            if result.details.score is None or result.details.score.current is None:
                upload_details = True
            if result.details.graphtarget is None:
                upload_details = True
            if result.details.graphtype == Graphtypes.GAUGE and result.details.options is None:
                upload_details = True
        
        if upload_details:
            self.storage.start_uploaddetails(image, result.play_side)
        
        return upload_informations and upload_details

    def checkandupload_resultothers(self, result:Result, image:Image.Image):
        if result.others.tab is None:
            return
        
        unrecognizeds = None
        if result.others.tab == ResultTabs.RIVAL:
            unrecognizeds = [
                result.others.rival.rankbefore is None,
                result.others.rival.ranknow is None,
                result.others.rival.rankposition is None,
            ]
        if result.others.tab == ResultTabs.RADAR:
            unrecognizeds = [
                result.others.notesradar.attribute is None,
                result.others.notesradar.chartvalue is None,
                result.others.notesradar.value is None,
            ]

        if not unrecognizeds or any(unrecognizeds):
            self.storage.start_uploadresultothers(image, result.play_side)
    
    def checkandupload_musicselect(self, image:Image):
        if self.musicselectchecker.evaluate():
            self.storage.start_uploadmusicselect(image)
    
    def checkandupload_notesradarvalue(self, npvalue:array):
        result = self.notesradarchecker.evaluate(npvalue)
        if result is not None:
            playmode = self.notesradarchecker.informations.play_mode
            songname = self.notesradarchecker.informations.music
            difficulty = self.notesradarchecker.informations.difficulty
            notes = self.notesradarchecker.informations.notes
            score = self.notesradarchecker.details.score.current

            ratio = Decimal(str(score / (notes * 2)))
            
            if not ratio:
                return
            
            attribute = result[0]
            chartvalue = Decimal(str(result[1]))

            predictedmaxlower = float((chartvalue/ratio).quantize(Decimal('0.00'), rounding=ROUND_UP))

            resourcemax = None
            r1 = resource.notesradar[playmode]
            if songname in r1['musics'].keys():
                r2 = r1['musics'][songname]
                if difficulty in r2.keys():
                    resourcemax = r2[difficulty]['radars'][attribute]
            
            if resourcemax is None or predictedmaxlower > resourcemax:
                self.storage.start_uploadnotesradarvalue({
                    'playmode': playmode,
                    'songname': songname,
                    'difficulty': difficulty,
                    'notes': notes,
                    'notesradar_attribute': attribute,
                    'score': score,
                    'notesradar_chartvalue': float(chartvalue),
                })
    
    def musicselectchecker_reset(self):
        self.musicselectchecker.reset()
    
    def notesradarchecker_reset(self):
        self.notesradarchecker.reset()
