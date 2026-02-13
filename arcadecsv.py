from json import dump,load
from os.path import isfile,join

from resources import resource
from record import records_basepath

filepaths = {
    'SP': join(records_basepath, 'arcadedata_sp.json'),
    'DP': join(records_basepath, 'arcadedata_dp.json'),
}

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

arcadedata = {
    'SP': None,
    'DP': None,
}

def import_arcadecsv(data: str) -> bool:
    if('\r\n' in data):
        lines = data.split('\r\n')
    else:
        lines = data.split('\n')
    
    headers = lines[0].split(',')
    if len(headers) != columncount:
        return False
    
    try:
        columnindex_normallevel = headers.index(headername_normallevel)
        columnindex_hyperlevel = headers.index(headername_hyperlevel)
    except Exception as ex:
        return False

    # プレイモードを自動判別
    playmode = None
    for line in lines[1:]:
        if len(line) == 0:
            continue

        values = line.split(',')
        if playmode is None:
            if values[1] in resource.musictable['musics']:
                music = resource.musictable['musics'][values[1]]
                try:
                    spnormal = music['SP']['NORMAL']
                    dpnormal = music['DP']['NORMAL']
                    if spnormal != dpnormal:
                        if spnormal == values[columnindex_normallevel]:
                            playmode = 'SP'
                        if dpnormal == values[columnindex_normallevel]:
                            playmode = 'DP'
                        break

                    sphyper = music['SP']['HYPER']
                    dphyper = music['DP']['HYPER']
                    if sphyper != dphyper:
                        if sphyper == values[columnindex_hyperlevel]:
                            playmode = 'SP'
                        if dphyper == values[columnindex_hyperlevel]:
                            playmode = 'DP'
                        break

                except Exception as ex:
                    pass
    
    if playmode is None:
        return False
    
    try:
        columnindex_musicname = headers.index(headername_musicname)

        columnindex_beginnerlevel = headers.index(headername_beginnerlevel)
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

    @staticmethod
    def converter(values, indexes):
        cleartype = values[indexes[2]]
        djlevel = values[indexes[3]]
        score = values[indexes[0]]
        misscount = values[indexes[1]]

        return {
            'cleartype': converter_cleartype[cleartype],
            'djlevel': djlevel if djlevel != '---' else None,
            'score': int(score) if score != '---' else None,
            'misscount': int(misscount) if misscount != '---' else None,
        }

    result = {}
    for line in lines[1:]:
        if len(line) == 0:
            continue

        values = line.split(',')
        if len(values) != columncount:
            return False
        
        musicname = values[columnindex_musicname]
        if not musicname in result.keys():
            result[musicname] = {}
        if values[columnindex_beginnerlevel] != '0':
            result[musicname]['BEGINNER'] = converter(values, columnindexes_beginner)
        if values[columnindex_normallevel] != '0':
            result[musicname]['NORMAL'] = converter(values, columnindexes_normal)
        if values[columnindex_hyperlevel] != '0':
            result[musicname]['HYPER'] = converter(values, columnindexes_hyper)
        if values[columnindex_anotherlevel] != '0':
            result[musicname]['ANOTHER'] = converter(values, columnindexes_another)
        if values[columnindex_leggendarialevel] != '0':
            result[musicname]['LEGGENDARIA'] = converter(values, columnindexes_leggendaria)

    with open(filepaths[playmode], 'w', encoding='utf-8') as f:
        dump(result, f)
    
    arcadedata[playmode] = result
    
    return True

def loadfiles_arcadedata() -> dict:
    for playmode, filepath in filepaths.items():
        if not isfile(filepath):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                value = load(f)
            arcadedata[playmode] = value
        except Exception as ex:
            pass
