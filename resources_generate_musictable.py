import json
from sys import exit
from os import mkdir
from os.path import join,basename,exists
from glob import glob
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from define import Playmodes,define
from image import generate_filename
from data_collection import collection_basepath
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname

label_filepath = join(collection_basepath, 'label_musicselect.json')

report_basedir_musictable = join(report_dirname, 'musictable')

version_unknown = 'Unknown'

versions_filename = 'versions.txt'
songnames_filename = 'songnames.csv'
infinitas_only_songnames_filename = 'infinitas_only_songnames.txt'

categorycount_versions_filename = 'categorycount_versions.csv'
categorycount_levels_filename = 'categorycount_levels.csv'
categorycount_difficulties_filename = 'categorycount_difficulties.csv'

versions_filepath = join(registries_dirname, versions_filename)
songnames_filepath = join(registries_dirname, songnames_filename)
infinitasonlysongnames_filepath = join(registries_dirname, infinitas_only_songnames_filename)

songnamefilenametest_basedir = join(report_dirname, 'songname_filename')

categorycount_versions_filepath = join(registries_dirname, categorycount_versions_filename)
categorycount_levels_filepath = join(registries_dirname, categorycount_levels_filename)
categorycount_difficulties_filepath = join(registries_dirname, categorycount_difficulties_filename)

arcade_scorefile_dirpaths = {
    Playmodes.SP: join(registries_dirname, 'originalscoredata_sp'),
    Playmodes.DP: join(registries_dirname, 'originalscoredata_dp'),
}

def load_arcade_scorefiles(report:Report):
    check_values = {
        'BEGINNER': 5,
        'NORMAL': 12,
        'HYPER': 19,
        'ANOTHER': 26,
        'LEGGENDARIA': 33,
    }

    report.append_log(f'load arcade scorefiles')

    arcadedata = {}

    for playmode, dirpath in arcade_scorefile_dirpaths.items():
        for filepath in glob(join(dirpath, '*.csv')):
            report.append_log(f'load {playmode}: {filepath}')
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.read().split('\n')
            
            for line in lines[1:]:
                splitted = line.split(',')
                if len(splitted) == 1 and len(splitted[0]) == 0:
                    continue
                if len(splitted) != 41:
                    report.append_log(f'error line: {line}')
                    break

                version = splitted[0]
                songname = splitted[1]

                if not songname in arcadedata.keys():
                    arcadedata[songname] = {'version': []}
                    for pm in Playmodes.values:
                        arcadedata[songname][pm] = {}
                        for key in check_values.keys():
                            arcadedata[songname][pm][key] = []
                
                arcadedata[songname]['version'].append({
                    'filename': basename(filepath),
                    'value': version,
                })

                for key, index in check_values.items():
                    if splitted[index] != '0':
                        arcadedata[songname][playmode][key].append({
                            'filename': basename(filepath),
                            'value': splitted[index],
                        })
    
    return arcadedata

def load_versions():
    with open(versions_filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
        lines.remove('')

    versions = {}
    for version in lines:
        versions[version] = []
    versions[version_unknown] = []

    return versions
    
def load_songnames(report:Report, table:dict, versions:dict):
    with open(songnames_filepath, 'r', encoding='utf-8') as f:
        songnames = f.read().split('\n')

    table['versions'] = {}
    for version in versions:
        table['versions'][version] = []
    
    table['musics'] = {}
    for line in songnames:
        if len(line) == 0:
            continue
        
        values = line.split(',')
        values = [','.join(values[:-2]), *values[-2:]]
        if len(values) != 3:
            report.error(f'line error: {values}')
            continue

        version = values[1]
        if not version in versions:
            report.error(f'version error: {version}')
            version = version_unknown

        songname = values[0]
        if songname == '':
            report.error(f'Music blank error: {line}')
            continue
        
        table['versions'][version].append(songname)
        table['musics'][songname] = {'version': version}
        for playmode in Playmodes.values:
            table['musics'][songname][playmode] = {}

def reflect_collections(report:Report, table:dict):
    try:
        with open(label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f'{label_filepath}を読み込めませんでした。')
        exit()

    output = []
    results = {}
    for key, item in labels.items():
        if not 'playmode' in item.keys() or item['playmode'] == '':
            continue
        if not 'version' in item.keys() or item['version'] == '':
            continue
        if not 'songname' in item.keys() or item['songname'] == '':
            continue
        if 'nohasscoredata' in item.keys() and item['nohasscoredata']:
            continue
        
        playmode = item['playmode']
        version = item['version']
        songname = item['songname']

        if not songname in table['musics'].keys():
            report.error(f'Not found song name: {songname}({key})')
            continue
        
        if version in ['1st', 'substream']:
            version = '1st&substream'

        if not version in table['versions'].keys():
            report.error(f'Not found version: {version}({key})')
            continue

        if not songname in table['versions'][version]:
            report.error(f'Wrong version: {version}({key})')
            continue
        
        if not songname in results.keys():
            results[songname] = {'SP': {}, 'DP': {}}
        
        for difficulty in define.value_list['difficulties']:
            labelkey = f'level_{str.lower(difficulty)}'
            if labelkey in item.keys() and item[labelkey] != '':
                level = item[labelkey]
                if not difficulty in results[songname][playmode].keys():
                    results[songname][playmode][difficulty] = {}
                results[songname][playmode][difficulty][key] = level
                table['musics'][songname][playmode][difficulty] = level
        
    for songname in results.keys():
        for playmode in results[songname].keys():
            for difficulty in results[songname][playmode].keys():
                if len(set(results[songname][playmode][difficulty].values())) != 1:
                    message = f'Duplicate level: {songname}[{playmode}{difficulty[0]}]'
                    report.error(message)
                    output.append(message)
                    for key in results[songname][playmode][difficulty].keys():
                        output.append(f'  {key}')
    
    if len(output) > 0:
        report.output_list(output, 'reflect collections.txt')

    table['levels'] = {}
    for playmode in Playmodes.values:
        table['levels'][playmode] = {}
        for level in define.value_list['levels']:
            table['levels'][playmode][level] = []
    
    table['beginners'] = []

    table['leggendarias'] = {}
    for playmode in Playmodes.values:
        table['leggendarias'][playmode] = []

    songnames = table['musics']
    for songname in songnames.keys():
        for playmode in Playmodes.values:
            for difficulty, level in songnames[songname][playmode].items():
                table['levels'][playmode][level].append({'music': songname, 'difficulty': difficulty})
                if playmode == 'SP' and difficulty == 'BEGINNER':
                    table['beginners'].append(songname)
                if difficulty == 'LEGGENDARIA':
                    table['leggendarias'][playmode].append(songname)

def evaluate_scoredata(report:Report, table:dict, arcadedata:dict):
    infinitas_only_songnames = []           # INFINITAS専用の曲
    arcade_only_songnames = []              # INFINITAS未収録のARCADE曲
    arcade_only_difficulty = []             # INFINITAS未収録の難易度
    infinitas_only_difficulty = []          # INFINITASのみの難易度
    reimportation_from_infinitas = []       # INFINITASからARCADEに逆輸入
    mismatch_level = []                     # ARCADEとレベルが違う

    if exists(infinitasonlysongnames_filepath):
        with open(infinitasonlysongnames_filepath, 'r', encoding='utf-8') as f:
            listed_infinitas_only_songnames = f.read().split('\n')
            listed_infinitas_only_songnames = [v for v in listed_infinitas_only_songnames if v != '']
    else:
        report.error(f'Not exists infinitas only songnames file: {infinitas_only_songnames_filename}')
        listed_infinitas_only_songnames = []
        
    for songname in listed_infinitas_only_songnames:
        if not songname in table['musics'].keys():
            report.error(f'Infinitas only list error: {songname}(Existing infinitas.)')

    for songname in arcadedata.keys():
        if not songname in table['musics'].keys():
            values = ','.join(set([v['value'] for v in arcadedata[songname]['version']]))
            arcade_only_songnames.append(f'- {songname}({values})')
        if songname in listed_infinitas_only_songnames:
            report.error(f'Infinitas only list error: {songname}(Existing arcade.)')
    
    for songname in table['musics'].keys():
        if not songname in arcadedata.keys():
            infinitas_only_songnames.append(f'- {songname} ({table['musics'][songname]['version']})')
            if not songname in listed_infinitas_only_songnames:
                report.error(f'Infinitas only list error: {songname}(Not included.)')
            continue
        
        versions = [*set([v['value'] for v in arcadedata[songname]['version']])]
        if len(versions) != 1:
            report.error(f'Duplicate arcade version {songname}')
            for v in arcadedata[songname]['version']:
                report.error(f'{v['filename']}: {v['value']}')
            continue
        
        version = versions[0]
        if not version in table['versions'].keys():
            report.error(f'Not defined {songname}: {version}')
            continue
        
        target = table['musics'][songname]

        if version != target['version']:
            if target['version'] == 'INFINITAS':
                reimportation_from_infinitas.append(f'- {songname}({version})')
                continue
            
            report.error(f'Wrong version {songname}: {target['version']}')
            continue

        for playmode in Playmodes.values:
            for difficulty in define.value_list['difficulties']:
                if difficulty in target[playmode].keys():
                    if len(arcadedata[songname][playmode][difficulty]) > 0:
                        uniques = [*set([v['value'] for v in arcadedata[songname][playmode][difficulty]])]
                        if len(uniques) != 1 or uniques[0] != table['musics'][songname][playmode][difficulty]:
                            levels = ','.join(uniques)
                            mismatch_level.append(f'- {songname}[{playmode}{difficulty[0]}]: {target[playmode][difficulty]} (ARCADE {levels} )')
                    else:
                        infinitas_only_difficulty.append(f'- {songname}[{playmode}{difficulty[0]}]')
                else:
                    if len(arcadedata[songname][playmode][difficulty]) > 0:
                        levels = ','.join(set([v['value'] for v in arcadedata[songname][playmode][difficulty]]))
                        arcade_only_difficulty.append(f'- {songname}[{playmode}{difficulty[0]}]: ARCADE {levels}')
    
    output = []
    if len(infinitas_only_songnames) > 0:
        output.extend([f'only infinitas({len(infinitas_only_songnames)})', *infinitas_only_songnames, ''])
    if len(infinitas_only_difficulty) > 0:
        output.extend([f'only infinitas difficulty({len(infinitas_only_difficulty)})', *infinitas_only_difficulty, ''])
    if len(reimportation_from_infinitas) > 0:
        output.extend([f'reimported from infinitas({len(reimportation_from_infinitas)})', *reimportation_from_infinitas, ''])
    if len(arcade_only_songnames) > 0:
        output.extend([f'only arcade({len(arcade_only_songnames)})', *arcade_only_songnames, ''])
    if len(arcade_only_difficulty) > 0:
        output.extend([f'only arcade difficulty({len(arcade_only_difficulty)})', *arcade_only_difficulty, ''])
    if len(mismatch_level) > 0:
        output.extend([f'mismatch level({len(mismatch_level)})', *mismatch_level, ''])
    
    if len(output) > 0:
        report.output_list(output, 'output.txt')

def evaluate_categories(report:Report, table:dict):
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
                report.error(f'{version} count NG: {len(versions[version])}, {count_versions[version]}')
        else:
            if len(versions[version]) > 0:
                report.error(f'mismatch version {version}: {len(versions[version])}')
        
        report.output_list(versions[version], f'version-{version}.txt')

    with open(categorycount_levels_filepath, 'r', encoding='utf-8') as f:
        count_levels = {'SP': {}, 'DP': {}}
        for line in f.read().split('\n'):
            if len(line) != 0:
                playmode, level, value = line.split(',')
                count_levels[playmode][level] = int(value)
    
    levels = table['levels']
    for playmode in Playmodes.values:
        for level in define.value_list['levels']:
            if len(levels[playmode][level]) == count_levels[playmode][level]:
                report.append_log(f'{playmode} {level} count: {len(levels[playmode][level])}')
            else:
                report.error(f'{playmode} {level} count NG: {len(levels[playmode][level])}, {count_levels[playmode][level]}')
            
            output = [f'{item['music']} {item['difficulty']}' for item in levels[playmode][level]]
            report.output_list(output, f'category-{playmode}-{level}.txt')
    
    with open(categorycount_difficulties_filepath, 'r', encoding='utf-8') as f:
        count_difficulties = {}
        for line in f.read().split('\n'):
            if len(line) != 0:
                key, value = line.split(',')
                count_difficulties[key] = int(value)
    
    beginners = table['beginners']
    if len(beginners) == count_difficulties['SPB']:
        report.append_log(f'SP BEGINNER count: {len(beginners)}')
    else:
        report.error(f'SP BEGINNER count NG: {len(beginners)}, {count_difficulties['SPB']}')
    
    report.output_list(beginners, f'category-beginner.txt')

    leggendarias = table['leggendarias']
    for playmode, target in [('SP', count_difficulties['SPL']), ('DP', count_difficulties['DPL'])]:
        if len(leggendarias[playmode]) == target:
            report.append_log(f'{playmode} LEGGENDARIA count: {len(leggendarias[playmode])}')
        else:
            report.error(f'{playmode} LEGGENDARIA count NG: {len(leggendarias[playmode])}, {target}')
        
        report.output_list(leggendarias[playmode], f'category-leggendaria-{playmode}.txt')

def filenametest(table:dict):
    songnames = table['musics']

    if not exists(songnamefilenametest_basedir):
        mkdir(songnamefilenametest_basedir)

    for songname in songnames:
        filename = generate_filename(None, songname, 'filenametest', filetype='txt')
        filepath = join(songnamefilenametest_basedir, filename)
        if not exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f'{songname}\n')
                f.write(f'{songname.encode('utf-8').hex()}\n')

def generate_musictable():
    versions = load_versions()

    report = Report('musictable')

    table = {}

    arcadedata = load_arcade_scorefiles(report)

    load_songnames(report, table, versions.keys())

    filenametest(table)

    reflect_collections(report, table)

    evaluate_scoredata(report, table, arcadedata)

    report.append_log(f'songname count: {len(table['musics'])}')

    evaluate_categories(report, table)
    
    filename = f'musictable{define.musictable_version}.res'
    save_resource_serialized(filename, table, True)

    report.output_json(table, 'result.json')
    report.report()

if __name__ == '__main__':
    generate_musictable()
