from os.path import join,exists
import json

from define import define
from resources import resource
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname

resource_filename = f'notesradar{define.notesradar_version}.res'

filenames = {
    'SP': join(registries_dirname, 'notesradardata_sp.csv'),
    'DP': join(registries_dirname, 'notesradardata_dp.csv')
}

ignore_filepath = join(registries_dirname, 'notesradar_ignore.json')

difficulties = {
    'B': 'BEGINNER',
    'N': 'NORMAL',
    'H': 'HYPER',
    'A': 'ANOTHER',
    'L': 'LEGGENDARIA'
}

report_name = 'notesradar'

def load_musictable():
    resource.load_resource_musictable()
    return resource.musictable

def import_csv():
    csv = {}
    for key, filename in filenames.items():
        if exists(filename):
            with open(filename, 'r', encoding='UTF-8') as f:
                csvdata = f.read().split('\n')
                splitted = [line.split(',') for line in csvdata]
                csv[key] = [[
                    s[1],
                    s[2].replace('""', '"'),
                    difficulties[s[4]],
                    s[5],
                    int(s[6]),
                    {
                        'NOTES': float(s[13]),
                        'CHORD': float(s[15]),
                        'PEAK': float(s[17]),
                        'CHARGE': float(s[19]),
                        'SCRATCH': float(s[21]),
                        'SOF-LAN': float(s[23])
                    }
                ] for s in splitted if len(s[1]) > 0 and s[1] != 'バージョン' and s[6].isdigit()]

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
    for playmode in define.value_list['play_modes']:
        resource[playmode] = {'musics': {}, 'attributes': {}}

    duplicate_difficulty = []
    added = {}
    for playmode in define.value_list['play_modes']:
        attribute_list = {}
        for attribute in define.value_list['notesradar_attributes']:
            attribute_list[attribute] = []

        for line in csv[playmode]:
            musicname = line[1]
            difficulty = line[2]
            notes = line[4]
            radars = line[5]
            
            if not musicname in musics.keys():
                continue

            if not difficulty in musics[musicname][playmode].keys():
                continue

            if musicname in ignore.keys() and playmode in ignore[musicname].keys() and difficulty in ignore[musicname][playmode]:
                report.append_log(f'Ignore {playmode} {musicname} {difficulty}')
                continue
            
            if musicname in added.keys() and playmode in added[musicname].keys() and difficulty in added[musicname][playmode]:
                duplicate_difficulty.append(f'{playmode} {musicname} {difficulty}')
                continue
            
            if not musicname in resource[playmode]['musics'].keys():
                resource[playmode]['musics'][musicname] = {}
            if not difficulty in resource[playmode]['musics'][musicname].keys():
                resource[playmode]['musics'][musicname][difficulty] = {
                    'notes': notes,
                    'radars': radars
                }

            for attribute, value in radars.items():
                if value != 0:
                    attribute_list[attribute].append({
                        'musicname': musicname,
                        'difficulty': difficulty,
                        'max': radars[attribute]
                    })

            if not musicname in added.keys():
                added[musicname] = {}
            if not playmode in added[musicname].keys():
                added[musicname][playmode] = []
            added[musicname][playmode].append(difficulty)
    
        for attribute in attribute_list.keys():
            attribute_list[attribute].sort(key=lambda t: t['max'], reverse=True)
            sorted_attributevalues = [{'musicname': t['musicname'], 'difficulty': t['difficulty']} for t in attribute_list[attribute]]
            resource[playmode]['attributes'][attribute] = sorted_attributevalues

    if len(duplicate_difficulty) > 0:
        report.error(f'Find duplicate difficulty: {len(duplicate_difficulty)}')
        for line in duplicate_difficulty:
            report.error(line)
    
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
