from os.path import join,exists
import json
from decimal import Decimal,ROUND_UP
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

import pandas as pd

from define import Playmodes,NotesradarAttributes,define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname
from data_collection import collection_basepath

resource_filename = f'notesradar{define.notesradar_version}.res'

radardata_dirpath = join(registries_dirname, 'notesradars')

radardata2_filepath = join(collection_basepath, 'notesradarvalues.json')

differentcharts_filepath = join(registries_dirname, 'different_chart.json')
convertsongnames_filepath = join(registries_dirname, 'notesradar_convertsongnames.json')

report_name = 'notesradar'

def generate():
    musics: dict = resource.musictable['musics']

    csvradardata = load_csvfiles()
    jsonradardata = load_collectiondata(radardata2_filepath)

    different_charts = load_json(differentcharts_filepath)
    convertsongnames = load_json(convertsongnames_filepath)

    result: dict[str, dict[str, dict[str, dict[str, int | dict[str, float]]]| dict[str, list[dict[str, str | int]]]]] = {}

    mismatch_notes = {}
    nousedsongnames = []
    for playmode in csvradardata.keys():
        result[playmode] = {'musics': {}, 'attributes': {}}
        mismatch_notes[playmode] = {}

        result_musics = result[playmode]['musics']
        for attribute in csvradardata[playmode].keys():
            result[playmode]['attributes'][attribute] = []

            df: pd.DataFrame = csvradardata[playmode][attribute]

            for row in df.itertuples():
                try:
                    songname = str(row.タイトル)
                    difficulty = str(row.難易度)
                    notes = int(row.ノーツ数)
                    value = float(row.MAX)
                except Exception as ex:
                    continue
                
                if songname in convertsongnames.keys():
                    songname = convertsongnames[songname]
                
                if not songname in musics.keys():
                    if not songname in nousedsongnames:
                        nousedsongnames.append(songname)
                    continue
                
                if songname in different_charts.keys():
                    if playmode in different_charts[songname].keys():
                        if difficulty in different_charts[songname][playmode]:
                            continue
                
                if not songname in result_musics.keys():
                    result_musics[songname] = {}

                if difficulty in result_musics[songname].keys():
                    if result_musics[songname][difficulty]['notes'] != notes:
                        if not songname in mismatch_notes[playmode].keys():
                            mismatch_notes[playmode][songname] = {}
                        if not difficulty in mismatch_notes[playmode][songname].keys():
                            mismatch_notes[playmode][songname][difficulty] = [result_musics[songname][difficulty]['notes']]

                        mismatch_notes[playmode][songname][difficulty].append(notes)
                        
                        continue
                
                if not difficulty in result_musics[songname].keys():
                    result_musics[songname][difficulty] = {
                        'notes': notes,
                        'radars': {}
                    }

                    for attribute1 in NotesradarAttributes.values:
                        result_musics[songname][difficulty]['radars'][attribute1] = 0
                
                result_musics[songname][difficulty]['radars'][attribute] = value

    for playmode in mismatch_notes.keys():
        if len(mismatch_notes[playmode]):
            report.error(f'Mismatch notes count: {playmode} {len(mismatch_notes[playmode])}')
            for songname in mismatch_notes[playmode].keys():
                for difficulty, value in mismatch_notes[playmode][songname].items():
                    report.append_log(f'  {songname}({difficulty}): {value}')

    uncertains = []
    overrides = []
    for playmode, target1 in jsonradardata.items():
        for songname, target2 in target1.items():
            for difficulty, target3 in target2.items():
                notes = target3['notes']
                for attribute in NotesradarAttributes.values:
                    predictedmaxlower = target3['attributes'][attribute]['lower']
                    predictedmaxupper = target3['attributes'][attribute]['upper']
                    
                    if predictedmaxlower != predictedmaxupper:
                        output = [songname, playmode, difficulty, attribute, f'{predictedmaxlower}～{predictedmaxupper}']
                        uncertains.append(' '.join(output))
                    
                    if not songname in result[playmode]['musics'].keys():
                        result[playmode]['musics'][songname] = {}
                    if not difficulty in result[playmode]['musics'][songname].keys():
                        result[playmode]['musics'][songname][difficulty] = {
                            'notes': notes,
                            'radars': {attribute: 0 for attribute in NotesradarAttributes.values},
                        }

                    registeredvalue = result[playmode]['musics'][songname][difficulty]['radars'][attribute]
                    if registeredvalue != 0:
                        if registeredvalue < predictedmaxlower:
                            output = [songname, playmode, difficulty, attribute, f'{registeredvalue}->{predictedmaxlower}']
                            overrides.append(' '.join(output))

                    result[playmode]['musics'][songname][difficulty]['radars'][attribute] = predictedmaxlower

    for playmode in Playmodes.values:
        result[playmode]['attributes'] = {}
        for attribute in NotesradarAttributes.values:
            rankingdata: dict[float, list[dict[str, str]]] = {}
            for songname in result[playmode]['musics'].keys():
                for difficulty in result[playmode]['musics'][songname].keys():
                    value = result[playmode]['musics'][songname][difficulty]['radars'][attribute]
                    if not value in rankingdata.keys():
                        rankingdata[value] = []
                    rankingdata[value].append({
                        'musicname': songname,
                        'difficulty': difficulty
                    })
        
            result[playmode]['attributes'][attribute] = []
            for value in reversed(sorted(rankingdata.keys())):
                result[playmode]['attributes'][attribute].extend(rankingdata[value])

    report.output_json(result, 'result.json')

    output_attributevalues(result)
    
    output_missings(musics, result)

    report.output_list(nousedsongnames, 'nousedsongnames.txt')

    report.output_list(uncertains, 'uncertains.txt')
    if len(uncertains):
        report.append_log(f'Has uncertains {len(uncertains)}')
    
    report.output_list(overrides, 'overrides.txt')
    if len(overrides):
        report.append_log(f'Has overrides {len(overrides)}')

    save_resource_serialized(resource_filename, result, True)

def load_csvfiles():
    data = {}
    for playmode in Playmodes.values:
        data[playmode] = {}
        for attribute in NotesradarAttributes.values:
            filename = join(radardata_dirpath, f'{playmode} {attribute}.csv')
            if exists(filename):
                data[playmode][attribute] = pd.read_csv(
                    filename,
                    keep_default_na=False,
                    encoding='utf-8',
                )

    return data

def load_json(filepath: str):
    if not exists(filepath):
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data
    
def load_collectiondata(filepath: str):
    if not exists(filepath):
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        loaddata = json.load(f)
    
    musics = resource.musictable['musics']

    data = {playmode: {} for playmode in Playmodes.values}

    format = Decimal('0.00')
    delta = Decimal('0.01')
    for key, values in loaddata.items():
        playmode = values['playmode']
        songname = values['songname']
        difficulty = values['difficulty']
        notes = values['notes']
        attribute = values['notesradar_attribute']
        score = values['score']
        chartvalue = Decimal(str(values['notesradar_chartvalue']))

        if not songname in musics.keys():
            report.error(f'Not exist from json data: {songname}({key})')
            continue
        if not difficulty in musics[songname][playmode].keys():
            report.error(f'Not exist from json data: {songname} {playmode} {difficulty}({key})')
            continue
        
        if not songname in data[playmode].keys():
            data[playmode][songname] = {}
        if not difficulty in data[playmode][songname].keys():
            data[playmode][songname][difficulty] = {'notes': notes, 'attributes': {}}
            for attribute1 in NotesradarAttributes.values:
                data[playmode][songname][difficulty]['attributes'][attribute1] = {
                    'lower': 0.00,
                    'upper': 200.00,
                }
        
        ratio = Decimal(str(score / (notes * 2)))

        predictedmaxlower = float((chartvalue/ratio).quantize(format, rounding=ROUND_UP))
        if predictedmaxlower > data[playmode][songname][difficulty]['attributes'][attribute]['lower']:
            data[playmode][songname][difficulty]['attributes'][attribute]['lower'] = predictedmaxlower

        predictedmaxupper = float(((chartvalue+delta)/ratio-delta).quantize(format, rounding=ROUND_UP))
        if predictedmaxupper < data[playmode][songname][difficulty]['attributes'][attribute]['upper']:
            data[playmode][songname][difficulty]['attributes'][attribute]['upper'] = predictedmaxupper

    return data

def output_attributevalues(resource: dict):
    for playmode, targets1 in resource.items():
        for attribute, targets2 in targets1['attributes'].items():
            output = []
            for target in targets2:
                musicname = target['musicname']
                difficulty = target['difficulty']

                value = resource[playmode]['musics'][musicname][difficulty]['radars'][attribute]
                output.append(f'{float(value):>6.2f}: {musicname}({difficulty})')
            
            filename = f'sorted_{playmode}_{attribute}.txt'

            report.output_list(output, filename)

def output_missings(musics: dict, result: dict):
    output = []
    for playmode in Playmodes.values:
        for songname in musics.keys():
            if not songname in result[playmode]['musics'].keys():
                output.append(f'{playmode} {songname}')
                continue
            
            for difficulty in musics[songname][playmode].keys():
                if not difficulty in result[playmode]['musics'][songname].keys():
                    output.append(f'{playmode} {songname} {difficulty}')
                    continue
                
                for attribute in NotesradarAttributes.values:
                    if not attribute in result[playmode]['musics'][songname][difficulty]['radars'].keys():
                        output.append(f'{playmode} {songname} {difficulty} {attribute}')

    report.output_list(output, 'missings.txt')

    if len(output):
        report.error(f'missings count: {len(output)}')

if __name__ == '__main__':
    report = Report(report_name)

    generate()

    report.report()
