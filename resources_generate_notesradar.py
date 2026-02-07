from os.path import join,exists
import json
import pandas as pd

from define import Playmodes,define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname
from resources_generate_musictable import infinitasonlymusics_filepath

resource_filename = f'notesradar{define.notesradar_version}.res'

radardata_dirpath = join(registries_dirname, 'notesradars')

filenames = {}
for playmode in Playmodes.values:
    filenames[playmode] = {}
    for attribute in define.value_list['notesradar_attributes']:
        filenames[playmode][attribute] = join(radardata_dirpath, f'{playmode} {attribute}.csv')

ignore_filepath = join(registries_dirname, 'notesradar_ignore.json')
convertmusicnames_filepath = join(registries_dirname, 'notesradar_convertmusicnames.json')

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
            
            csv[playmode][attribute] = pd.read_csv(
                filename,
                keep_default_na=False,
                encoding='UTF-8'
            )

    return csv

def output_attributevalues(resource: dict, output_dirpath: str):
    for playmode, targets1 in resource.items():
        for attribute, targets2 in targets1['attributes'].items():
            output = []
            for target in targets2:
                musicname = target['musicname']
                difficulty = target['difficulty']

                value = resource[playmode]['musics'][musicname][difficulty]['radars'][attribute]
                output.append(f'{float(value):>6.2f}: {musicname}({difficulty})')
                
            filename = f'{playmode}_{attribute}.txt'
            filepath = join(output_dirpath, filename)

            with open(filepath, 'w', encoding='UTF-8') as f:
                f.write('\n'.join(output))

def output_not_in_notesradar(added: dict, musics: dict, ignore: dict, output_dirpath: str):
    if exists(infinitasonlymusics_filepath):
        with open(infinitasonlymusics_filepath, 'r', encoding='UTF-8') as f:
            infinitas_only_musics = [v for v in f.read().split('\n') if v != '']
    else:
        infinitas_only_musics = []

    output = []
    for musicname in musics.keys():
        if not musicname in added.keys():
            if not musicname in infinitas_only_musics and not musicname in ignore.keys():
                output.append(f'{musicname}')
            continue
        
        for playmode in Playmodes.values:
            if not playmode in added[musicname].keys():
                if musicname in ignore.keys():
                    includes = [*musics[musicname][playmode].keys()]
                    addeds = ignore[musicname][playmode]
                    if not len(includes) == len(addeds) and all([d in addeds for d in includes]):
                        output.append(f'{musicname} {playmode}')
                continue

            for difficulty in musics[musicname][playmode].keys():
                if not difficulty in added[musicname][playmode].keys():
                    if musicname in ignore.keys() and not difficulty in ignore[musicname][playmode]:
                        output.append(f'{musicname} {playmode} {difficulty}')

    not_in_notesradar_music_filepath = join(output_dirpath, 'not_in_notesradar.csv')
    with open(not_in_notesradar_music_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def generate(musics, csv):
    report = Report(report_name)

    if exists(ignore_filepath):
        with open(ignore_filepath, 'r', encoding='UTF-8') as f:
            ignore = json.load(f)
    else:
        ignore = {}
    
    if exists(convertmusicnames_filepath):
        with open(convertmusicnames_filepath, 'r', encoding='UTF-8') as f:
            convertmusicnames = json.load(f)
    else:
        convertmusicnames = []
    
    resource: dict[str, dict[str, dict[str, dict[str, int | dict[str, float]]]| dict[str, list[dict[str, str | int]]]]] = {}

    added = {}
    mismatch_notes = {}

    nas = [music for music in musics if 'n/a' in music]

    for playmode in csv.keys():
        resource[playmode] = {'musics': {}, 'attributes': {}}
        mismatch_notes[playmode] = {}

        notesradar_musics = resource[playmode]['musics']
        for attribute in csv[playmode].keys():
            resource[playmode]['attributes'][attribute] = []
            notesradar_attribute = resource[playmode]['attributes'][attribute]

            df: pd.DataFrame = csv[playmode][attribute]

            for row in df.itertuples():
                try:
                    musicname = str(row.タイトル)
                    difficulty = str(row.難易度)
                    notes = int(row.ノーツ数)
                    value = float(row.MAX)
                except Exception as ex:
                    continue

                if musicname in convertmusicnames.keys():
                    musicname = convertmusicnames[musicname]
                
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
                    added[musicname][playmode] = {}
                if not difficulty in added[musicname][playmode].keys():
                    added[musicname][playmode][difficulty] = []
                added[musicname][playmode][difficulty].append(attribute)

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
            for musicname in mismatch_notes[playmode].keys():
                for difficulty, value in mismatch_notes[playmode][musicname].items():
                    report.append_log(f'  {musicname}({difficulty}): {value}')

    report.report()

    output_attributevalues(resource, report.report_dirpath)
    
    output_not_in_notesradar(added, musics, ignore, report.report_dirpath)

    return resource

def generate_notesradar():
    csv = import_csv()

    data = generate(resource.musictable['musics'], csv)

    save_resource_serialized(resource_filename, data, True)

if __name__ == '__main__':
    generate_notesradar()
