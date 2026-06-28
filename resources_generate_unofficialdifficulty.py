from os.path import join,isfile,sep
import json
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

import json5

from define import define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname

NOUSESONGNAMES_FILENAME = 'nousesongnames.txt'

resource_filename = f'unofficialdifficulty{define.unofficialdifficulty_version}.res'

difficultydata_dirpath = join(registries_dirname, 'unofficialdifficulties')

source_dirnames_filepath = join(registries_dirname, 'unofficialdifficulty_dirnames.txt')
with open(source_dirnames_filepath, 'r', encoding='utf-8') as f:
    dirnames = f.read().split('\n')

difficultydata_filepaths = [join(join(difficultydata_dirpath, dirname), 'result.json') for dirname in dirnames if len(dirname)]

differentchart_filepath = join(registries_dirname, 'different_chart.json5')

output_filepath = join(difficultydata_dirpath, 'output.json')

report_name = 'unofficialdifficulty'

report = Report(report_name)

def loadfile(filepath: str):
    key = filepath.split(sep)[-2]
    if not isfile(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for playtype in data.keys():
        for songname in data[playtype].keys():
            if not songname in musictable['musics'].keys():
                nousesongnames.append(f'{key}\t{playtype}\t{songname}')
                continue

            for difficulty in data[playtype][songname].keys():
                playmode = playtype if not 'BATTLE' in playtype else 'DP'

                if not playmode in musictable['musics'][songname].keys():
                    continue
                if not difficulty in musictable['musics'][songname][playmode].keys():
                    continue

                if songname in differentcharts.keys():
                    if playmode in differentcharts[songname].keys():
                        if difficulty in differentcharts[songname][playmode]:
                            continue
                
                if not songname in result.keys():
                    result[songname] = {}
                if not playtype in result[songname].keys():
                    result[songname][playtype] = {}
                if not difficulty in result[songname][playtype].keys():
                    result[songname][playtype][difficulty] = []
                
                result[songname][playtype][difficulty].extend(data[playtype][songname][difficulty])

if __name__ == '__main__':
    musictable = resource.musictable

    if isfile(differentchart_filepath):
        with open(differentchart_filepath, 'r', encoding='utf-8') as f:
            differentcharts = json5.load(f)
    else:
        differentcharts = {}
    
    result = {}
    nousesongnames = []

    for filepath in difficultydata_filepaths:
        loadfile(filepath)

    save_resource_serialized(resource_filename, result, True)

    report.output_list(nousesongnames, NOUSESONGNAMES_FILENAME)

    report.output_json(result, 'result.json')

    report.report()
