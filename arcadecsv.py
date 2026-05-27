from pickle import dump,load
from os.path import isfile,join
import gzip
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from define import Playmodes,define
from resources import resource
from record import records_basepath

filepath = join(records_basepath, 'arcadedata.gz')

versions = list(resource.musictable['versions'].keys())
versions = versions[versions.index('copula'):]
versions.remove('INFINITAS')
versions.remove('Unknown')

columncount = 41

headername_musicname = 'タイトル'
headername_beginnerlevel = 'BEGINNER 難易度'
headername_beginnerscore = 'BEGINNER スコア'
headername_beginnermisscount = 'BEGINNER ミスカウント'
headername_beginnercleartype = 'BEGINNER クリアタイプ'
headername_beginnerdjlevel = 'BEGINNER DJ LEVEL'
headername_normallevel = 'NORMAL 難易度'
headername_normalscore = 'NORMAL スコア'
headername_normalmisscount = 'NORMAL ミスカウント'
headername_normalcleartype = 'NORMAL クリアタイプ'
headername_normaldjlevel = 'NORMAL DJ LEVEL'
headername_hyperlevel = 'HYPER 難易度'
headername_hyperscore = 'HYPER スコア'
headername_hypermisscount = 'HYPER ミスカウント'
headername_hypercleartype = 'HYPER クリアタイプ'
headername_hyperdjlevel = 'HYPER DJ LEVEL'
headername_anotherlevel = 'ANOTHER 難易度'
headername_anotherscore = 'ANOTHER スコア'
headername_anothermisscount = 'ANOTHER ミスカウント'
headername_anothercleartype = 'ANOTHER クリアタイプ'
headername_anotherdjlevel = 'ANOTHER DJ LEVEL'
headername_leggendarialevel = 'LEGGENDARIA 難易度'
headername_leggendariascore = 'LEGGENDARIA スコア'
headername_leggendariamisscount = 'LEGGENDARIA ミスカウント'
headername_leggendariacleartype = 'LEGGENDARIA クリアタイプ'
headername_leggendariadjlevel = 'LEGGENDARIA DJ LEVEL'

class ArcadeData():
    data: dict[str, dict[str, dict]] = {}

    @staticmethod
    def converter(values, indexes):
        cleartype = values[indexes[2]]
        djlevel = values[indexes[3]]
        score = values[indexes[0]]
        misscount = values[indexes[1]]

        converter_cleartype = {
            'FULLCOMBO CLEAR': 'F-COMBO',
            'EX HARD CLEAR': 'EXH-CLEAR',
            'HARD CLEAR': 'H-CLEAR',
            'CLEAR': 'CLEAR',
            'EASY CLEAR': 'E-CLEAR',
            'ASSIST CLEAR': 'A-CLEAR',
            'FAILED': 'FAILED',
            'NO PLAY': 'NO PLAY',
            '---': None,
        }

        return {
            'cleartype': converter_cleartype[cleartype],
            'djlevel': djlevel if djlevel != '---' else None,
            'score': int(score) if score != '---' else None,
            'misscount': int(misscount) if misscount != '---' else None,
        }

    def __init__(self):
        if not isfile(filepath):
            return

        try:
            with gzip.open(filepath, 'rb',) as f:
                self.data = load(f)
        except Exception as ex:
            logger.exception(ex)
    
    def import_csv(self, data:str, playmode:str, version:str) -> bool:
        if not playmode in Playmodes.values:
            return False

        if not version in resource.musictable['versions'].keys():
            return False
        
        headers = data[0].split(',')
        if len(headers) != columncount:
            return False
        
        try:
            columnindex_musicname = headers.index(headername_musicname)

            columnindex_beginnerlevel = headers.index(headername_beginnerlevel)
            columnindex_normallevel = headers.index(headername_normallevel)
            columnindex_hyperlevel = headers.index(headername_hyperlevel)
            columnindex_anotherlevel = headers.index(headername_anotherlevel)
            columnindex_leggendarialevel = headers.index(headername_leggendarialevel)

            columnindexes_beginner = [
                headers.index(headername_beginnerscore),
                headers.index(headername_beginnermisscount),
                headers.index(headername_beginnercleartype),
                headers.index(headername_beginnerdjlevel),
            ]

            columnindexes_normal = [
                headers.index(headername_normalscore),
                headers.index(headername_normalmisscount),
                headers.index(headername_normalcleartype),
                headers.index(headername_normaldjlevel),
            ]

            columnindexes_hyper = [
                headers.index(headername_hyperscore),
                headers.index(headername_hypermisscount),
                headers.index(headername_hypercleartype),
                headers.index(headername_hyperdjlevel),
            ]

            columnindexes_another = [
                headers.index(headername_anotherscore),
                headers.index(headername_anothermisscount),
                headers.index(headername_anothercleartype),
                headers.index(headername_anotherdjlevel),
            ]

            columnindexes_leggendaria = [
                headers.index(headername_leggendariascore),
                headers.index(headername_leggendariamisscount),
                headers.index(headername_leggendariacleartype),
                headers.index(headername_leggendariadjlevel),
            ]

        except Exception as ex:
            return False

        result = {}
        for line in data[1:]:
            if len(line) == 0:
                continue

            values = line.split(',')
            if len(values) != columncount:
                return False
            
            musicname = values[columnindex_musicname]
            if not musicname in result.keys():
                result[musicname] = {}
            if values[columnindex_beginnerlevel] != '0':
                result[musicname]['BEGINNER'] = self.converter(values, columnindexes_beginner)
            if values[columnindex_normallevel] != '0':
                result[musicname]['NORMAL'] = self.converter(values, columnindexes_normal)
            if values[columnindex_hyperlevel] != '0':
                result[musicname]['HYPER'] = self.converter(values, columnindexes_hyper)
            if values[columnindex_anotherlevel] != '0':
                result[musicname]['ANOTHER'] = self.converter(values, columnindexes_another)
            if values[columnindex_leggendarialevel] != '0':
                result[musicname]['LEGGENDARIA'] = self.converter(values, columnindexes_leggendaria)

        if not playmode in self.data.keys():
            self.data[playmode] = {}
        self.data[playmode][version] = result

        with gzip.open(filepath, 'wb') as f:
            dump(self.data, f)
        
        return True

    def get(self, playmode:str, songname:str, difficulty:str) -> dict:
        if not playmode in self.data.keys():
            return None
        
        ret = {'best': None, 'histories': {}}

        bests = {
            'cleartype': {'index': None, 'version': None},
            'djlevel': {'index': None, 'version': None},
            'score': {'value': None, 'version': None},
            'misscount': {'value': None, 'version': None},
        }
        for version in versions:
            if not version in self.data[playmode].keys():
                continue

            versiondata = self.data[playmode][version]
            if songname in versiondata.keys() and difficulty in versiondata[songname].keys():
                targetdata = versiondata[songname][difficulty]

                if targetdata['cleartype'] in define.value_list['clear_types']:
                    targetcleartypeindex = define.value_list['clear_types'].index(targetdata['cleartype'])
                    if bests['cleartype']['index'] is None or bests['cleartype']['index'] < targetcleartypeindex:
                        bests['cleartype']['index'] = targetcleartypeindex
                        bests['cleartype']['version'] = version
                if targetdata['djlevel'] in define.value_list['dj_levels']:
                    targetdjlevelindex = define.value_list['dj_levels'].index(targetdata['djlevel'])
                    if bests['djlevel']['index'] is None or bests['djlevel']['index'] < targetdjlevelindex:
                        bests['djlevel']['index'] = targetdjlevelindex
                        bests['djlevel']['version'] = version
                if targetdata['score'] is not None and (bests['score']['value'] is None or bests['score']['value'] < targetdata['score']):
                    bests['score']['value'] = targetdata['score']
                    bests['score']['version'] = version
                if targetdata['misscount'] is not None and (bests['misscount']['value'] is None or bests['misscount']['value'] > targetdata['misscount']):
                    bests['misscount']['value'] = targetdata['misscount']
                    bests['misscount']['version'] = version
                
                ret['histories'][version] = targetdata
        
        ret['best'] = {
            'cleartype': {
                'value': define.value_list['clear_types'][bests['cleartype']['index']] if bests['cleartype']['index'] is not None else None,
                'version': bests['cleartype']['version'],
            },
            'djlevel': {
                'value': define.value_list['dj_levels'][bests['djlevel']['index']] if bests['djlevel']['index'] is not None else None,
                'version': bests['djlevel']['version'],
            },
            'score': {
                'value': bests['score']['value'],
                'version': bests['score']['version'],
            },
            'misscount': {
                'value': bests['misscount']['value'],
                'version': bests['misscount']['version'],
            },
        }

        return ret