from os.path import join

from define import define
from resources_generate import Report,registries_dirname

version_unknown = 'Unknown'

trimmed_difficulties_sp_filename = 'trimmed_difficulties_sp.csv'
trimmed_difficulties_dp_filename = 'trimmed_difficulties_dp.csv'
versions_filename = 'versions.txt'
musiclist_filename = 'musics.csv'
categorycount_versions_filename = 'categorycount_versions.csv'
categorycount_levels_filename = 'categorycount_levels.csv'
categorycount_difficulties_filename = 'categorycount_difficulties.csv'

trimmed_difficulties_sp_filepath = join(registries_dirname, trimmed_difficulties_sp_filename)
trimmed_difficulties_dp_filepath = join(registries_dirname, trimmed_difficulties_dp_filename)
versions_filepath = join(registries_dirname, versions_filename)
musiclist_filepath = join(registries_dirname, musiclist_filename)
categorycount_versions_filepath = join(registries_dirname, categorycount_versions_filename)
categorycount_levels_filepath = join(registries_dirname, categorycount_levels_filename)
categorycount_difficulties_filepath = join(registries_dirname, categorycount_difficulties_filename)

def load_musiclist(report):
    with open(versions_filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
        lines.remove("")

    versions = {}
    for version in lines:
        versions[version] = []
    versions[version_unknown] = []
    
    with open(musiclist_filepath, 'r', encoding='utf-8') as f:
        musiclist = f.read().split('\n')

    musics = {}
    for line in musiclist:
        if len(line) == 0:
            continue
        
        values = line.split(',')
        values = [','.join(values[:-11]), *values[-11:]]
        if len(values) != 12:
            report.error(f'line error: {values}')
            continue

        version = values[1]
        if not version in versions.keys():
            report.error(f'version error: {version}')
            version = version_unknown

        music = values[0]
        if music == '':
            report.error(f'Music blank error: {line}')
        
        versions[version].append(music)
        musics[music] = {'version': version}
        for play_mode in define.value_list['play_modes']:
            musics[music][play_mode] = {}
    
        index = 2
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                if values[index] != '-':
                    musics[music][play_mode][difficulty] = values[index] if values[index] != '0' else None
                index += 1

    return versions, musics

def reflect_collections_analyzed(report, versions, musics, analyzed):
    for music in analyzed.keys():
        version = version_unknown
        for key, value in versions.items():
            if music in value:
                version = key
                break

        if version == version_unknown:
            versions[version].append(music)
            musics[music] = {'version': version_unknown}
            for play_mode in define.value_list['play_modes']:
                musics[music][play_mode] = {}
        
        for play_mode in analyzed[music].keys():
            for difficulty, value in analyzed[music][play_mode].items():
                if difficulty in musics[music][play_mode].keys():
                    if musics[music][play_mode][difficulty] is not None:
                        if value == musics[music][play_mode][difficulty]:
                            report.append_log(f"In collections {music} {play_mode} {difficulty}: {value}")
                        else:
                            report.error(f"Mismatch {version} {music} {play_mode} {difficulty}: {value}, {musics[music][play_mode][difficulty]}")
                else:
                    musics[music][play_mode][difficulty] = value

def reflect_scoredata(versions, musics, play_mode, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        scoredata = f.read().split('\n')

    for line in scoredata:
        music, version, beginner, normal, hyper, another, leggendaria = line.split(',')

        if not version in versions.keys():
            continue

        if not music in musics.keys():
            continue

        if beginner != '0' and not 'BEGINNER' in musics[music][play_mode].keys():
            musics[music][play_mode]['BEGINNER'] = beginner
        if normal != '0' and not 'NORMAL' in musics[music][play_mode].keys():
            musics[music][play_mode]['NORMAL'] = normal
        if hyper != '0' and not 'HYPER' in musics[music][play_mode].keys():
            musics[music][play_mode]['HYPER'] = hyper
        if another != '0' and not 'ANOTHER' in musics[music][play_mode].keys():
            musics[music][play_mode]['ANOTHER'] = another
        if leggendaria != '0' and not 'LEGGENDARIA' in musics[music][play_mode].keys():
            musics[music][play_mode]['LEGGENDARIA'] = leggendaria

def generate(analyzed, reportdir):
    report = Report('musictable')

    versions, musics = load_musiclist(report)

    reflect_collections_analyzed(report, versions, musics, analyzed)

    reflect_scoredata(versions, musics, 'SP', trimmed_difficulties_sp_filepath)
    reflect_scoredata(versions, musics, 'DP', trimmed_difficulties_dp_filepath)

    report.append_log(f'Total count: {len(musics)}')

    report_versions = []
    for version in versions.keys():
        report_versions.append(f'{version}: {len(versions[version])}')
        for music in versions[version]:
            levels = []
            for play_mode in define.value_list['play_modes']:
                for difficulty in define.value_list['difficulties']:
                    if difficulty in musics[music][play_mode].keys() and musics[music][play_mode][difficulty] is not None:
                        levels.append(f'{play_mode}{difficulty[0]}{musics[music][play_mode][difficulty]}')
            report_versions.append(f"  {music}: {' '.join(levels)}")

    report_filepath = join(reportdir, 'musictable_versions.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_versions))

    beginners = {}
    for play_mode in define.value_list['play_modes']:
        beginners[play_mode] = {}
        for music in musics.keys():
            if 'BEGINNER' in musics[music][play_mode].keys() and musics[music][play_mode]['BEGINNER'] is not None:
                beginners[play_mode][music] = musics[music][play_mode]['BEGINNER']

    report_beginners = []
    for play_mode in define.value_list['play_modes']:
        report_beginners.append(f'{play_mode}: {len(beginners[play_mode])}')
        report_beginners.extend([f'  {key}: {value}' for key, value in beginners[play_mode].items()])

    report_filepath = join(reportdir, 'musictable_beginners.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_beginners))

    leggendarias = {}
    for play_mode in define.value_list['play_modes']:
        leggendarias[play_mode] = {}
        for music in musics.keys():
            if 'LEGGENDARIA' in musics[music][play_mode].keys() and musics[music][play_mode]['LEGGENDARIA'] is not None:
                leggendarias[play_mode][music] = musics[music][play_mode]['LEGGENDARIA']

    report_leggendarias = []
    for play_mode in define.value_list['play_modes']:
        report_leggendarias.append(f'{play_mode}: {len(leggendarias[play_mode])}')
        report_leggendarias.extend([f'  {key}: {value}' for key, value in leggendarias[play_mode].items()])

    report_filepath = join(reportdir, 'musictable_leggendarias.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_leggendarias))

    levels = {}
    for play_mode in define.value_list['play_modes']:
        levels[play_mode] = {}
        for level in define.value_list['levels']:
            levels[play_mode][level] = []
        for music in musics.keys():
            for difficulty in define.value_list['difficulties']:
                if difficulty in musics[music][play_mode].keys() and musics[music][play_mode][difficulty] != None:
                    level = musics[music][play_mode][difficulty]
                    try:
                        levels[play_mode][level].append({'music': music, 'difficulty': difficulty})
                    except Exception as ex:
                        report.error(f'Musics error?? {music}: {ex}')

    report_levels = []
    for play_mode in define.value_list['play_modes']:
        for level in define.value_list['levels']:
            report_levels.append(f'{play_mode} level {level}: {len(levels[play_mode][level])}')
            for values in levels[play_mode][level]:
                report_levels.append(f"  {values['music']} {values['difficulty']}")

    report_filepath = join(reportdir, 'musictable_levels.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_levels))

    with open(categorycount_versions_filepath, 'r', encoding='utf-8') as f:
        count_versions = {}
        for line in f.read().split('\n'):
            if len(line) != 0:
                key, value = line.split(',')
                count_versions[key] = int(value)
    
    for version in versions.keys():
        if version in count_versions.keys():
            if len(versions[version]) != count_versions[version]:
                report.error(f"{version} count NG: {len(versions[version])}, {count_versions[version]}")
        else:
            if len(versions[version]) > 0:
                report.error(f"mismatch version {version}: {len(versions[version])}")

    with open(categorycount_levels_filepath, 'r', encoding='utf-8') as f:
        count_levels = {'SP': {}, 'DP': {}}
        for line in f.read().split('\n'):
            if len(line) != 0:
                play_mode, level, value = line.split(',')
                count_levels[play_mode][level] = int(value)
    
    for play_mode in define.value_list['play_modes']:
        for level in define.value_list['levels']:
            if len(levels[play_mode][level]) != count_levels[play_mode][level]:
                report.error(f"{play_mode} {level} count NG: {len(levels[play_mode][level])}, {count_levels[play_mode][level]}")
    
    with open(categorycount_difficulties_filepath, 'r', encoding='utf-8') as f:
        count_difficulties = {}
        for line in f.read().split('\n'):
            if len(line) != 0:
                key, value = line.split(',')
                count_difficulties[key] = int(value)
    
    if len(beginners['SP']) != count_difficulties['SPB']:
        report.error(f"SP BEGINNER count NG: {len(beginners['SP'])}, {count_difficulties['SPB']}")

    if len(leggendarias['SP']) != count_difficulties['SPL']:
        report.error(f"SP LEGGENDARIA count NG: {len(leggendarias['SP'])}, {count_difficulties['SPL']}")

    if len(leggendarias['DP']) != count_difficulties['DPL']:
        report.error(f"DP LEGGENDARIA count NG: {len(leggendarias['DP'])}, {count_difficulties['SPL']}")

    report.report()
    
    return {
        'musics': musics,
        'versions': versions,
        'levels': levels,
    }

if __name__ == '__main__':
    report = Report('musictable')
    load_musiclist(report)
