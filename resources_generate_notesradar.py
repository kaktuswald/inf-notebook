import json
from os import listdir
from os.path import join,exists,isdir
from decimal import Decimal,ROUND_UP
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

import pandas as pd

from define import Playmodes,NotesradarAttributes,define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname
from data_collection import collection_basepath

resource_filename = f'notesradar{define.notesradar_version}.res'

registerdata_dirpath = join(registries_dirname, 'notesradars')
registerdata_filepath = join(registerdata_dirpath, 'notesradar.csv')

collectiondata_filepath = join(collection_basepath, 'notesradarvalues.json')

differentcharts_filepath = join(registries_dirname, 'different_chart.json')
convertsongnames_filepath = join(registries_dirname, 'notesradar_convertsongnames.json')

report_name = 'notesradar'

def generate():
    musics: dict = resource.musictable['musics']

    registerdata = []
    for filename in listdir(registerdata_dirpath):
        filepath = join(registerdata_dirpath, filename)
        if isdir(filepath):
            registerdata.append(
                pd.read_csv(
                    join(filepath, 'notesradar.csv'),
                    keep_default_na=False,
                    encoding='utf-8',
                )
            )
    
    collectiondata = load_collectiondata(collectiondata_filepath)

    different_charts = load_json(differentcharts_filepath)
    convertsongnames = load_json(convertsongnames_filepath)

    result: dict[str, dict[str, dict[str, dict[str, int | dict[str, float]]]| dict[str, list[dict[str, str | int]]]]] = {}

    nousedsongnames = []
    for data in registerdata:
        for i, row in data.iterrows():
            playmode = row['playmode']
            if not playmode in result.keys():
                result[playmode] = {'musics': {}}
            
            title = row['title']
            songname = convertsongnames[title] if title in convertsongnames.keys() else title

            if not songname in musics.keys():
                if not songname in nousedsongnames:
                    nousedsongnames.append(songname)
                continue

            if not songname in result[playmode]['musics'].keys():
                result[playmode]['musics'][songname] = {}

            difficulty = row['difficulty']
            if not difficulty in musics[songname][playmode].keys():
                continue

            if songname in different_charts.keys():
                if playmode in different_charts[songname].keys():
                    if difficulty in different_charts[songname][playmode]:
                        continue

            if not songname in result[playmode]['musics'].keys():
                result[playmode]['musics'][songname] = {}
            
            notes = row['notes']
            if not notes:
                continue

            result[playmode]['musics'][songname][difficulty] = {
                'notes': int(notes),
                'radars': {
                    'NOTES': float(row['NOTES']) if row['NOTES'] else 0,
                    'CHORD': float(row['CHORD']) if row['CHORD'] else 0,
                    'PEAK': float(row['PEAK']) if row['PEAK'] else 0,
                    'CHARGE': float(row['CHARGE']) if row['CHARGE'] else 0,
                    'SCRATCH': float(row['SCRATCH']) if row['SCRATCH'] else 0,
                    'SOF-LAN': float(row['SOF-LAN']) if row['SOF-LAN'] else 0,
                },
            }

    uncertains = []
    overrides = []
    for playmode, target1 in collectiondata.items():
        for songname, target2 in target1.items():
            if not songname in result[playmode]['musics'].keys():
                result[playmode]['musics'][songname] = {}
            
            for difficulty, target3 in target2.items():
                if not difficulty in result[playmode]['musics'][songname].keys():
                    result[playmode]['musics'][songname][difficulty] = {
                        'notes': target3['notes'],
                        'radars': {attribute: 0 for attribute in NotesradarAttributes.values},
                    }

                for attribute in target3['attributes'].keys():
                    predictedmaxlower = target3['attributes'][attribute]['lower']
                    predictedmaxupper = target3['attributes'][attribute]['upper']
                    
                    if predictedmaxlower != predictedmaxupper:
                        output = [songname, playmode, difficulty, attribute, f'{predictedmaxlower}～{predictedmaxupper}']
                        uncertains.append(' '.join(output))
                    
                    registeredvalue = result[playmode]['musics'][songname][difficulty]['radars'][attribute]
                    if registeredvalue != 0:
                        if registeredvalue < predictedmaxlower:
                            output = [songname, playmode, difficulty, attribute, f'{registeredvalue}->{predictedmaxlower}']
                            overrides.append(' '.join(output))

                    result[playmode]['musics'][songname][difficulty]['radars'][attribute] = predictedmaxlower

    for playmode in Playmodes.values:
        for songradars in result[playmode]['musics'].values():
            for chartvalue in songradars.values():
                maxvalue = max(chartvalue['radars'].values())
                chartvalue['attributes'] = [key for key, value in chartvalue['radars'].items() if value == maxvalue]

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
        if not attribute in data[playmode][songname][difficulty]['attributes'].keys():
            data[playmode][songname][difficulty]['attributes'][attribute] = {
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
