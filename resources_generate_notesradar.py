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
report_basedir = join(report_dirname, report_name)

def load_musictable():
    resource.load_resource_musictable()
    return resource.musictable

def import_csv():
    csv = {}
    for key, filename in filenames.items():
        if exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
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

def generate(musics, csv):
    report = Report(report_name)

    if exists(ignore_filepath):
        with open(ignore_filepath, 'r', encoding='UTF-8') as f:
            ignore = json.load(f)
    else:
        ignore = {}
    
    resource = {}
    duplicate_difficulty = []
    for playmode in define.value_list['play_modes']:
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
            
            if not musicname in resource.keys():
                resource[musicname] = {'SP': {}, 'DP': {}}
            
            if difficulty in resource[musicname][playmode].keys():
                duplicate_difficulty.append(f'{playmode} {musicname} {difficulty}')
                continue

            resource[musicname][playmode][difficulty] = (notes, radars)
    
    not_in_notesradar_music = []
    not_in_notesradar_difficulty = {}
    for playmode in define.value_list['play_modes']:
        not_in_notesradar_difficulty[playmode] = {}
    for musicname in musics.keys():
        if not musicname in resource.keys():
            not_in_notesradar_music.append(musicname)
            continue
        for playmode in define.value_list['play_modes']:
            for difficulty in musics[musicname][playmode].keys():
                if not difficulty in resource[musicname][playmode].keys():
                    if not musicname in not_in_notesradar_difficulty[playmode].keys():
                        not_in_notesradar_difficulty[playmode][musicname] = []
                    if not difficulty in resource[musicname][playmode].keys():
                        not_in_notesradar_difficulty[playmode][musicname].append(difficulty)

    report.append_log(f'no data music count: {len(not_in_notesradar_music)}')
    for playmode in not_in_notesradar_difficulty.keys():
        counts = [len(values) for values in not_in_notesradar_difficulty[playmode].values()]
        report.append_log(f'no data difficulty count {playmode}: {sum(counts)}')

    if len(duplicate_difficulty) > 0:
        report.error(f'Find duplicate difficulty: {len(duplicate_difficulty)}')
        for line in duplicate_difficulty:
            report.error(line)
    
    report.report()

    not_in_notesradar_music_filepath = join(report_basedir, 'not_in_notesradar.csv')
    output = []
    output.append('Music')
    for musicname in not_in_notesradar_music:
        output.append(f'- {musicname}')
    output.append('')
    for playmode in not_in_notesradar_difficulty.keys():
        output.append(f'Difficulty {playmode}')
        for musicname in not_in_notesradar_difficulty[playmode].keys():
            for difficulty in not_in_notesradar_difficulty[playmode][musicname]:
                output.append(f'- {musicname} {difficulty}')
        output.append('')

    with open(not_in_notesradar_music_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

    return resource

def generate_notesradar():
    musictable = load_musictable()
    csv = import_csv()
    resource = generate(musictable['musics'], csv)

    save_resource_serialized(resource_filename, resource)

if __name__ == '__main__':
    generate_notesradar()
