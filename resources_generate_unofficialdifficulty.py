from os.path import join,isfile
from json import load

from define import define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname

resource_filename = f'unofficialdifficulty{define.unofficialdifficulty_version}.res'

difficultydata_dirpath = join(registries_dirname, 'unofficialdifficulties')

difficultydata_filepaths = [
    join(join(difficultydata_dirpath, 'spwiki'), 'result.json'),
]

differentchart_filepath = join(registries_dirname, 'different_chart.json')

output_filepath = join(difficultydata_dirpath, 'output.json')

report_name = 'unofficialdifficulty'

report = Report(report_name)

def loadfile(filepath: str):
    if not isfile(filepath):
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = load(f)
    
    for playtype in data.keys():
        for songname in data[playtype].keys():
            for difficulty in data[playtype][songname].keys():
                playmode = playtype if not 'BATTLE' in playtype else 'DP'

                if not songname in musictable['musics'].keys():
                    continue
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
            differentcharts = load(f)
    else:
        differentcharts = {}
    
    result = {}

    for filepath in difficultydata_filepaths:
        loadfile(filepath)

    save_resource_serialized(resource_filename, result, True)

    report.output_json(result, 'result.json')

    report.report()
