import json
from sys import exit
from os.path import join

from define import define
from data_collection import collection_basepath
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname

label_filepath = join(collection_basepath, 'label_musicselect.json')

report_basedir_musictable = join(report_dirname, 'musictable')

version_unknown = 'Unknown'

versions_filename = 'versions.txt'
musiclist_filename = 'musics.csv'

categorycount_versions_filename = 'categorycount_versions.csv'
categorycount_levels_filename = 'categorycount_levels.csv'
categorycount_difficulties_filename = 'categorycount_difficulties.csv'

versions_filepath = join(registries_dirname, versions_filename)
musiclist_filepath = join(registries_dirname, musiclist_filename)

categorycount_versions_filepath = join(registries_dirname, categorycount_versions_filename)
categorycount_levels_filepath = join(registries_dirname, categorycount_levels_filename)
categorycount_difficulties_filepath = join(registries_dirname, categorycount_difficulties_filename)

def load_versions():
    with open(versions_filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
        lines.remove("")

    versions = {}
    for version in lines:
        versions[version] = []
    versions[version_unknown] = []

    return versions
    
def load_musiclist(report, table, versions):
    with open(musiclist_filepath, 'r', encoding='utf-8') as f:
        musiclist = f.read().split('\n')

    table['versions'] = {}
    for version in versions:
        table['versions'][version] = []
    
    table['musics'] = {}
    for line in musiclist:
        if len(line) == 0:
            continue
        
        values = line.split(',')
        values = [','.join(values[:-11]), *values[-11:]]
        if len(values) != 12:
            report.error(f'line error: {values}')
            continue

        version = values[1]
        if not version in versions:
            report.error(f'version error: {version}')
            version = version_unknown

        music = values[0]
        if music == '':
            report.error(f'Music blank error: {line}')
        
        table['versions'][version].append(music)
        table['musics'][music] = {'version': version}
        for play_mode in define.value_list['play_modes']:
            table['musics'][music][play_mode] = {}

def reflect_collections(report, table):
    try:
        with open(label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{label_filepath}を読み込めませんでした。")
        exit()

    output = []
    results = {}
    for key, item in labels.items():
        if not 'playmode' in item.keys() or item['playmode'] == '':
            continue
        if not 'version' in item.keys() or item['version'] == '':
            continue
        if not 'musicname' in item.keys() or item['musicname'] == '':
            continue
        
        playmode = item['playmode']
        version = item['version']
        musicname = item['musicname']

        if not musicname in table['musics'].keys():
            report.error(f'Not found music name: {musicname}({key})')
            continue
        
        if version in ['1st', 'substream']:
            version = '1st&substream'

        if not version in table['versions'].keys():
            report.error(f'Not found version: {version}({key})')
            continue

        if not musicname in table['versions'][version]:
            report.error(f'Wrong version: {version}({key})')
            continue
        
        if not musicname in results.keys():
            results[musicname] = {'SP': {}, 'DP': {}}
        
        for difficulty in define.value_list['difficulties']:
            labelkey = f'level_{str.lower(difficulty)}'
            if labelkey in item.keys() and item[labelkey] != '':
                level = item[labelkey]
                if not difficulty in results[musicname][playmode].keys():
                    results[musicname][playmode][difficulty] = {}
                results[musicname][playmode][difficulty][key] = level
                table['musics'][musicname][playmode][difficulty] = level
        
    for musicname in results.keys():
        for playmode in results[musicname].keys():
            for difficulty in results[musicname][playmode].keys():
                if len(set(results[musicname][playmode][difficulty].values())) != 1:
                    message = f'Duplicate level: {musicname}[{playmode}{difficulty[0]}]'
                    report.error(message)
                    output.append(message)
                    for key in results[musicname][playmode][difficulty].keys():
                        output.append(f'  {key}')
    
    if len(output) > 0:
        output_filepath = join(report_basedir_musictable, 'reflect collections.txt')
        with open(output_filepath, 'w', encoding='UTF-8') as f:
            f.write('\n'.join(output))

    table['levels'] = {}
    for playmode in define.value_list['play_modes']:
        table['levels'][playmode] = {}
        for level in define.value_list['levels']:
            table['levels'][playmode][level] = []
    
    table['beginners'] = []

    table['leggendarias'] = {}
    for playmode in define.value_list['play_modes']:
        table['leggendarias'][playmode] = []

    musics = table['musics']
    for musicname in musics.keys():
        for playmode in define.value_list['play_modes']:
            for difficulty, level in musics[musicname][playmode].items():
                table['levels'][playmode][level].append({'music': musicname, 'difficulty': difficulty})
                if playmode == 'SP' and difficulty == 'BEGINNER':
                    table['beginners'].append(musicname)
                if difficulty == 'LEGGENDARIA':
                    table['leggendarias'][playmode].append(musicname)

def evaluate_scoredata(report, table):
    arcade_only_music = []  # INFINITAS未収録のARCADE曲
    arcade_only_difficulty = {}  # INFINITAS未収録の難易度
    reimportation_from_infinitas = []  # INFINITASからARCADEに逆輸入
    mismatch_level = []    # ARCADEとレベルが違う
    for playmode in define.value_list['play_modes']:
        filename = f'trimmed_difficulties_{str.lower(playmode)}.csv'
        filepath = join(registries_dirname, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            scoredata = f.read().split('\n')

        for line in scoredata:
            musicname, version, beginner, normal, hyper, another, leggendaria = line.split(',')

            if not musicname in table['musics'].keys():
                arcade_only_music.append(f'- {musicname}({version})')
                continue

            if not version in table['versions'].keys():
                report.error(f'Not defined {musicname}: {version}')
                continue

            if version != table['musics'][musicname]['version']:
                if table['musics'][musicname]['version'] == 'INFINITAS':
                    reimportation_from_infinitas.append(f'- {musicname}({version})')
                    continue

                report.error(f"Wrong version {musicname}: {table['musics'][musicname]['version']}")
                continue

            target = table['musics'][musicname][playmode]
            levels = {
                'BEGINNER': beginner,
                'NORMAL': normal,
                'HYPER': hyper,
                'ANOTHER': another,
                'LEGGENDARIA': leggendaria,
            }
            for key, level in levels.items():
                if level != '0':
                    if not key in target.keys():
                        if not playmode in arcade_only_difficulty.keys():
                            arcade_only_difficulty[playmode] = {}
                        if not key in arcade_only_difficulty[playmode].keys():
                            arcade_only_difficulty[playmode][key] = []
                        arcade_only_difficulty[playmode][key].append(f"- - {musicname}({table['musics'][musicname]['version']})")
                        continue
                    if target[key] != level:
                        mismatch_level.append(f'- {musicname}[{playmode}{key[0]}]: {target[key]} (ARCADE {level} )')
                        continue
    
    output = []
    if len(arcade_only_music) > 0:
        output.extend([f'arcade only music({len(arcade_only_music)})', *arcade_only_music, ''])
    if len(arcade_only_difficulty) > 0:
        output.append('arcade only difficulty:')
        for playmode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                if playmode in arcade_only_difficulty.keys() and difficulty in arcade_only_difficulty[playmode].keys():
                    output.extend([f'- {playmode} {difficulty}({len(arcade_only_difficulty[playmode][difficulty])})', *arcade_only_difficulty[playmode][difficulty], ''])
    if len(reimportation_from_infinitas) > 0:
        output.extend([f'reimported from infinitas({len(reimportation_from_infinitas)})', *reimportation_from_infinitas, ''])
    if len(mismatch_level) > 0:
        output.extend([f'mismatch level({len(mismatch_level)})', *mismatch_level, ''])
    
    if len(output) > 0:
        output_filepath = join(report_basedir_musictable, 'output.txt')
        with open(output_filepath, 'w', encoding='UTF-8') as f:
            f.write('\n'.join(output))
    
def evaluate_categories(report, table):
    with open(categorycount_versions_filepath, 'r', encoding='utf-8') as f:
        count_versions = {}
        for line in f.read().split('\n'):
            if len(line) != 0:
                key, value = line.split(',')
                count_versions[key] = int(value)
    
    versions = table['versions']
    for version in versions.keys():
        if version in count_versions.keys():
            if len(versions[version]) != count_versions[version]:
                report.error(f"{version} count NG: {len(versions[version])}, {count_versions[version]}")
        else:
            if len(versions[version]) > 0:
                report.error(f"mismatch version {version}: {len(versions[version])}")
        filename = f'version-{version}.txt'
        filepath = join(report_basedir_musictable, filename)
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write('\n'.join(versions[version]))


    with open(categorycount_levels_filepath, 'r', encoding='utf-8') as f:
        count_levels = {'SP': {}, 'DP': {}}
        for line in f.read().split('\n'):
            if len(line) != 0:
                playmode, level, value = line.split(',')
                count_levels[playmode][level] = int(value)
    
    levels = table['levels']
    for playmode in define.value_list['play_modes']:
        for level in define.value_list['levels']:
            if len(levels[playmode][level]) == count_levels[playmode][level]:
                report.append_log(f"{playmode} {level} count: {len(levels[playmode][level])}")
            else:
                report.error(f"{playmode} {level} count NG: {len(levels[playmode][level])}, {count_levels[playmode][level]}")
            filename = f'category-{playmode}-{level}.txt'
            filepath = join(report_basedir_musictable, filename)
            with open(filepath, 'w', encoding='UTF-8') as f:
                f.write('\n'.join([f"{item['music']} {item['difficulty']}" for item in levels[playmode][level]]))
    
    with open(categorycount_difficulties_filepath, 'r', encoding='utf-8') as f:
        count_difficulties = {}
        for line in f.read().split('\n'):
            if len(line) != 0:
                key, value = line.split(',')
                count_difficulties[key] = int(value)
    
    beginners = table['beginners']
    if len(beginners) == count_difficulties['SPB']:
        report.append_log(f'SP BEGINER count: {len(beginners)}')
    else:
        report.error(f"SP BEGINNER count NG: {len(beginners)}, {count_difficulties['SPB']}")
    filename = f'category-beginner.txt'
    filepath = join(report_basedir_musictable, filename)
    with open(filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(beginners))

    leggendarias = table['leggendarias']
    for playmode, target in [('SP', count_difficulties['SPL']), ('DP', count_difficulties['DPL'])]:
        if len(leggendarias[playmode]) == target:
            report.append_log(f'{playmode} LEGGENDARIA count: {len(leggendarias[playmode])}')
        else:
            report.error(f'{playmode} LEGGENDARIA count NG: {len(leggendarias[playmode])}, {target}')
        filename = f'category-leggendaria-{playmode}.txt'
        filepath = join(report_basedir_musictable, filename)
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write('\n'.join(leggendarias[playmode]))

def generate_musictable():
    versions = load_versions()

    report = Report('musictable')

    table = {}

    load_musiclist(table, table, versions.keys())

    reflect_collections(report, table)

    evaluate_scoredata(report, table)

    report.append_log(f"music count: {len(table['musics'])}")

    evaluate_categories(report, table)
    
    filename = f'musictable{define.musictable_version}.res'
    save_resource_serialized(filename, table)

    report.report()

if __name__ == '__main__':
    generate_musictable()
