from os.path import join,exists
import json
import pandas as pd

from define import define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname

resource_filename = f'notesradar{define.notesradar_version}.res'

radardata_dirpath = join(registries_dirname, 'notesradars')

filenames = {}
for playmode in define.value_list['play_modes']:
    filenames[playmode] = {}
    for attribute in define.value_list['notesradar_attributes']:
        filenames[playmode][attribute] = join(radardata_dirpath, f'{playmode} {attribute}.csv')

ignore_filepath = join(registries_dirname, 'notesradar_ignore.json')

report_name = 'notesradar'

def load_musictable():
    resource.load_resource_musictable()
    return resource.musictable

def import_csv():
    csv = {}
    for playmode in filenames.keys():
        csv[playmode] = {}
        for attribute in filenames[playmode].keys():

            filename = filenames[playmode][attribute]
            if not exists(filename):
                continue

            csv[playmode][attribute] = pd.read_csv(filename, encoding='UTF-8')

    return csv

def output_attributevalues(resource: dict, output_dirpath: str):
    for playmode, targets1 in resource.items():
        for attribute, targets2 in targets1['attributes'].items():
            output = []
            for target in targets2:
                musicname = target['musicname']
                difficulty = target['difficulty']

                value = resource[playmode]['musics'][musicname][difficulty]['radars'][attribute]
                output.append(f'{value:>6.2f}: {musicname}({difficulty})')
                
            filename = f'{playmode}_{attribute}.txt'
            filepath = join(output_dirpath, filename)

            with open(filepath, 'w', encoding='UTF-8') as f:
                f.write('\n'.join(output))

def output_not_in_notesradar(added: dict, musics: dict, output_dirpath: str):
    not_in_notesradar_music_filepath = join(output_dirpath, 'not_in_notesradar.csv')
    output = []
    output.append('Music')
    output.append('\n'.join([f'- {musicname}' for musicname in musics.keys() if not musicname in added.keys()]))
    output.append('')
    for playmode in define.value_list['play_modes']:
        output.append(f'Difficulty {playmode}')
        for musicname in musics.keys():
            if musicname in added.keys() and playmode in added[musicname].keys():
                for difficulty in musics[musicname][playmode].keys():
                    if not difficulty in added[musicname][playmode]:
                        output.append(f'- {musicname} {difficulty}')
        output.append('')

    with open(not_in_notesradar_music_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def generate(musics, csv):
    report = Report(report_name)

    if exists(ignore_filepath):
        with open(ignore_filepath, 'r', encoding='UTF-8') as f:
            ignore = json.load(f)
    else:
        ignore = {}
    
    resource: dict[str, dict[str, dict[str, dict[str, int | dict[str, float]]]| dict[str, list[dict[str, str | int]]]]] = {}

    added = {}
    mismatch_notes = {}

    for playmode in csv.keys():
        resource[playmode] = {'musics': {}, 'attributes': {}}
        mismatch_notes[playmode] = {}

        notesradar_musics = resource[playmode]['musics']
        for attribute in csv[playmode].keys():
            resource[playmode]['attributes'][attribute] = []
            notesradar_attribute = resource[playmode]['attributes'][attribute]

            df: pd.DataFrame = csv[playmode][attribute]

            for row in df.itertuples():
                musicname = row.タイトル
                difficulty = row.難易度
                notes = row.ノーツ数
                value = row.MAX

                if not musicname in musics.keys():
                    continue

                if musicname in ignore.keys():
                    if playmode in ignore[musicname].keys():
                        if difficulty in ignore[musicname][playmode]:
                            report.append_log(f'Ignore {playmode} {musicname} {difficulty} {attribute}')
                            continue

                if not musicname in notesradar_musics.keys():
                    notesradar_musics[musicname] = {}
                    if not musicname in added.keys():
                        added[musicname] = {}

                if difficulty in notesradar_musics[musicname].keys():
                    if notesradar_musics[musicname][difficulty]['notes'] != notes:
                        if not musicname in mismatch_notes[playmode].keys():
                            mismatch_notes[playmode][musicname] = {}
                        if not difficulty in mismatch_notes[playmode][musicname].keys():
                            mismatch_notes[playmode][musicname][difficulty] = [notesradar_musics[musicname][difficulty]['notes']]

                        mismatch_notes[playmode][musicname][difficulty].append(notes)
                        
                        continue
                
                if not playmode in added[musicname].keys():
                    added[musicname][playmode] = []
                added[musicname][playmode].append(difficulty)

                if not difficulty in notesradar_musics[musicname].keys():
                    notesradar_musics[musicname][difficulty] = {
                        'notes': notes,
                        'radars': {}
                    }

                    for attribute1 in define.value_list['notesradar_attributes']:
                        notesradar_musics[musicname][difficulty]['radars'][attribute1] = 0
                
                notesradar_musics[musicname][difficulty]['radars'][attribute] = value

                notesradar_attribute.append({
                    'musicname': musicname,
                    'difficulty': difficulty,
                })

    for playmode in mismatch_notes.keys():
        if len(mismatch_notes[playmode]):
            report.append_log(f'Mismatch notes count: {playmode} {len(mismatch_notes[playmode])}')

    report.report()

    output_attributevalues(resource, report.report_dirpath)
    output_not_in_notesradar(added, musics, report.report_dirpath)

    return resource

def generate_notesradar():
    musictable = load_musictable()
    csv = import_csv()
    resource = generate(musictable['musics'], csv)

    save_resource_serialized(resource_filename, resource)

if __name__ == '__main__':
    generate_notesradar()
