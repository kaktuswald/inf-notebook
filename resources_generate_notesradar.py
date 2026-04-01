from os.path import join,exists
import json
import pandas as pd

from define import Playmodes,NotesradarAttributes,define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname
from resources_generate_musictable import infinitasonlymusics_filepath
from data_collection import collection_basepath

resource_filename = f'notesradar{define.notesradar_version}.res'

radardata_dirpath = join(registries_dirname, 'notesradars')

radardata2_filepath = join(collection_basepath, 'notesradarvalues.json')

differentcharts_filepath = join(registries_dirname, 'different_chart.json')
convertmusicnames_filepath = join(registries_dirname, 'notesradar_convertmusicnames.json')

report_name = 'notesradar'

def generate():
    musics: dict = resource.musictable['musics']

    csvradardata = load_csvfiles()
    jsonradardata = load_json(radardata2_filepath)
    different_charts = load_json(differentcharts_filepath)
    convertmusicnames = load_json(convertmusicnames_filepath)

    result: dict[str, dict[str, dict[str, dict[str, int | dict[str, float]]]| dict[str, list[dict[str, str | int]]]]] = {}

    mismatch_notes = {}
    for playmode in csvradardata.keys():
        result[playmode] = {'musics': {}, 'attributes': {}}
        mismatch_notes[playmode] = {}

        result_musics = result[playmode]['musics']
        for attribute in csvradardata[playmode].keys():
            result[playmode]['attributes'][attribute] = []
            result_attribute = result[playmode]['attributes'][attribute]

            df: pd.DataFrame = csvradardata[playmode][attribute]

            for row in df.itertuples():
                try:
                    songname = str(row.タイトル)
                    difficulty = str(row.難易度)
                    notes = int(row.ノーツ数)
                    value = float(row.MAX)
                except Exception as ex:
                    continue
                
                if songname in convertmusicnames.keys():
                    songname = convertmusicnames[songname]
                
                if not songname in musics.keys():
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

                result_attribute.append({
                    'musicname': songname,
                    'difficulty': difficulty,
                })

    for playmode in mismatch_notes.keys():
        if len(mismatch_notes[playmode]):
            report.error(f'Mismatch notes count: {playmode} {len(mismatch_notes[playmode])}')
            for songname in mismatch_notes[playmode].keys():
                for difficulty, value in mismatch_notes[playmode][songname].items():
                    report.append_log(f'  {songname}({difficulty}): {value}')

    uncertains = []
    overrides = []
    for key, data in jsonradardata.items():
        playmode = data['playmode']
        songname = data['songname']
        difficulty = data['difficulty']
        notes = data['notes']
        attribute = data['notesradar_attribute']
        score = data['score']
        chartvalue = data['notesradar_chartvalue']

        if not songname in musics.keys():
            report.error(f'Not exist {songname}({key})')
            continue
        if not difficulty in musics[songname][playmode].keys():
            report.error(f'Not exist {songname} {playmode} {difficulty}({key})')
            continue
    
        ratio = score / (notes * 2)

        predictedmaxlower = float(f'{chartvalue/ratio:.2f}')
        predictedmaxupper = float(f'{((chartvalue+0.01)/ratio)-0.01:.2f}')

        if predictedmaxlower != predictedmaxupper:
            output = [songname, playmode, difficulty, attribute, f'{predictedmaxlower}～{predictedmaxupper}']
            uncertains.append(f'{key}: {songname} {' '.join(output)}')
        
        if not songname in result[playmode]['musics'].keys():
            result[playmode]['musics'][songname] = {}
        if not difficulty in result[playmode]['musics'][songname].keys():
            result[playmode]['musics'][songname][difficulty] = {
                'notes': notes,
                'radars': {attribute: 0 for attribute in NotesradarAttributes.values},
            }
        
        registeredvalue = result[playmode]['musics'][songname][difficulty]['radars'][attribute]
        if registeredvalue != 0:
            if registeredvalue < predictedmaxlower or registeredvalue > predictedmaxupper:
                output = [songname, playmode, difficulty, attribute, f'{registeredvalue}->{predictedmaxlower}']
                overrides.append(f'{key}: {' '.join(output)}')
        
        result[playmode]['musics'][songname][difficulty]['radars'][attribute] = predictedmaxlower

    report.output_json(result, 'result.json')

    output_attributevalues(result)
    
    output_missings(musics, result)

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
