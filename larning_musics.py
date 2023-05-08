from PIL import Image
import json
from sys import exit
from os import mkdir,remove
from os.path import join,isfile,exists
import numpy as np
from glob import glob
from scipy.stats import mode
import time

from define import define
from resources import recog_musics_filepath
import data_collection as dc
from larning import create_resource_directory

recognition_define_filename = 'musics_recognition_define.json'

background_ignore_keys_filename = 'background_ignore_keys.txt'

dirname = 'larning_music'

backgrounds_report_filepath = join(dirname, 'backgrounds_report.txt')
mask_report_filepath = join(dirname, 'mask_report.txt')
not_unique_report_filepath = join(dirname, 'not_unique_report.txt')
mask_imagepath = join(dirname, 'mask.png')

if not exists(dirname):
    mkdir(dirname)

music_inspection_basepath = join(dirname, 'inspection')

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'
registered_musics_filename = 'musics_registered.txt'
missing_musics_filename = 'musics_missing_in_arcade.txt'

class InformationsImage():
    def __init__(self, background_key, np_value, music):
        self.background_key = background_key
        self.np_value = np_value
        self.music = music

def load_recognition_define():
    if not isfile(recognition_define_filename):
        print(f"{recognition_define_filename}が見つかりませんでした。")
        return None
    
    try:
        with open(recognition_define_filename) as f:
            recog_define = json.load(f)
    except Exception:
        print(f"{recognition_define_filename}を読み込めませんでした。")
        return None
    
    return recog_define

def load_images(recog_define, keys, labels):
    background_key_position = tuple(recog_define['background_key_position'])
    area = recog_define['trimarea']

    images = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if isfile(filepath):
            image = Image.open(filepath)
            if image.height == 75:
                image = image.crop((0, 3, image.width, image.height - 1)).convert('L')
            if image.height == 78:
                image = image.crop((0, 5, image.width, image.height - 2)).convert('L')
            images[key] = InformationsImage(
                image.getpixel(background_key_position),
                np.array(image)[area[1]:area[3], area[0]:area[2]],
                labels[key]['informations']['music']
            )

    return images
    
def generate_backgrounds(shape, images, ignore_keys):
    background_sources = {}
    report = {}
    added_musics = {}
    for key, image in images.items():
        if key in ignore_keys:
            continue
        if not image.background_key in background_sources.keys():
            background_sources[image.background_key] = []
            added_musics[image.background_key] = []
            report[image.background_key] = []
        if not image.music in added_musics[image.background_key]:
            background_sources[image.background_key].append(image.np_value)
            report[image.background_key].append([key, image.music])
            added_musics[image.background_key].append(image.music)

    print('background sources')
    backgrounds = {}
    for background_key in sorted(background_sources.keys()):
        stacks = np.stack(background_sources[background_key])
        result, counts = mode(stacks, keepdims=True)
        result_background = result.reshape(shape)

        backgrounds[background_key] = result_background

        print(f'{background_key:03}: {len(background_sources[background_key])}')
    
    with open(backgrounds_report_filepath, 'w', encoding='UTF-8') as f:
        for bkey in sorted(report.keys()):
            reports = report[bkey]
            for r in reports:
                f.write(f'({bkey:3}){r[0]}: {r[1]}\n')

    return backgrounds

def larning(recog_define, images, backgrounds):
    originals = {}
    for key, image in [*images.items()]:
        if not image.music in originals.keys():
            originals[image.music] = {}
        originals[image.music][key] = image

    np_values = {}

    trimarea = recog_define['trimarea']
    width = trimarea[2] - trimarea[0]
    gray_filter = np.tile(np.array(recog_define['gray_thresholds']), (width, 1)).T

    filtereds = {}
    for music in originals.keys():
        filtereds[music] = {}
        for key, image in originals[music].items():
            np_values[key] = []

            background_key = image.background_key
            np_value = image.np_value
            np_values[key].append(np_value)

            background_removed = np.where(backgrounds[background_key]!=np_value, np_value, 0)
            np_values[key].append(background_removed)

            gray_filtered = np.where(background_removed>=gray_filter, background_removed, 0)
            np_values[key].append(gray_filtered)

            filtereds[music][key] = gray_filtered

    shape = (trimarea[3]-trimarea[1], trimarea[2]-trimarea[0])

    mask = np.full(shape, False, dtype='bool')
    mask_report = {}
    for music in filtereds.keys():
        background_matches = []
        for key, current in filtereds[music].items():
            stacked = np.stack([np.where(current!=target, True, False) for target in filtereds[music].values()])
            result = np.any(stacked, axis=0)
            mismatch = np.where(result, images[key].np_value, 0)
            background_match = np.where(mismatch==backgrounds[images[key].background_key], True, False)
            background_matches.append(background_match)
        match_result = np.any(np.stack(background_matches), axis=0)
        mask = np.where(match_result, True, mask)
        mask_report[music] = np.stack(np.where(match_result)).T

    image_mask = Image.fromarray(mask).convert('L')
    image_mask.save(mask_imagepath)

    with open(mask_report_filepath, 'w', encoding='UTF-8') as f:
        for music in sorted(mask_report.keys()):
            if len(mask_report[music]) != 0:
                f.write(f"({len(originals[music]):2}:{len(mask_report[music]):2}){music}: {' '.join([str(p) for p in mask_report[music]])}\n")

    map_keys = {}
    map = {}

    for music in filtereds.keys():
        for key, filtered in filtereds[music].items():
            masked = np.where(mask, 0, filtered)
            np_values[key].append(masked)

            maxcounts = []
            maxcount_values = []
            for line in masked:
                unique, counts = np.unique(line, return_counts=True)
                if len(counts) != 1:
                    index = -np.argmax(np.flip(counts[1:])) - 1
                    maxcounts.append(counts[index])
                    maxcount_values.append(unique[index])
                else:
                    maxcounts.append(0)
                    maxcount_values.append(0)

            mapkeys = []
            for y in np.argsort(maxcounts)[::-1]:
                color = int(maxcount_values[y])
                bins = np.where(masked[y]==color, 1, 0)
                hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
                mapkeys.append(f"{y:02d}{''.join([format(v, '0x') for v in hexs])}")
            
            map_keys[key] = mapkeys

            target = map
            for k in mapkeys:
                if len(target) == 0:
                    target['musics'] = {}
                    target['keys'] = {}

                if not music in target['musics'].keys():
                    target['musics'][music] = []
                target['musics'][music].append(key)

                if not k in target['keys'].keys():
                    target['keys'][k] = {}
                target = target['keys'][k]
            if len(target) == 0:
                target['musics'] = {}
                target['keys'] = {}

            if not music in target['musics'].keys():
                target['musics'][music] = []
            target['musics'][music].append(key)
    
    inspect_targets = []

    result = {}
    report = {}
    def optimization(resulttarget, maptarget):
        if len(maptarget['musics']) >= 2:
            if len(maptarget['keys']) == 0:
                musics = [m for m in maptarget['musics'].keys()]
                print('duplicate', musics)
                for m in musics:
                    print(f"{m}: {maptarget['musics'][m]}")
                inspect_targets.extend(musics)
            else:
                for key in maptarget['keys'].keys():
                    resulttarget[key] = {}
                    music = optimization(resulttarget[key], maptarget['keys'][key])
                    if music is not None:
                        resulttarget[key] = music
            return None
        else:
            music = [*maptarget['musics'].keys()][0]
            music_keys = maptarget['musics'].values()
            resulttarget = music
            if not music in report.keys():
                report[music] = []
            report[music].append(*music_keys)
            return music
    optimization(result, map)

    not_uniques = []
    for music, keys in [*report.items()]:
        if len(keys) >= 2:
            if len(inspect_targets) < 2:
                print('not unique', music, keys)
                inspect_targets.append(music)
            not_uniques.append(f'({len(keys):2}){music}:')
            for k in keys:
                not_uniques.append(f"{' '.join(k)}")

    with open(not_unique_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(not_uniques))

    if len(inspect_targets) > 0:
        for filepath in glob(join(music_inspection_basepath, '*.png')):
            try:
                remove(filepath)
            except Exception as ex:
                print(ex)

        for background_key in backgrounds.keys():
            output_image = Image.fromarray(backgrounds[background_key])
            output_filepath = join(music_inspection_basepath, f'_background_{background_key}.png')
            output_image.save(output_filepath)

        if not exists(music_inspection_basepath):
            mkdir(music_inspection_basepath)

        for music in inspect_targets[:2]:
            escape_music_name = music.replace('"', '')
            escape_music_name = escape_music_name.replace('/', '')
            escape_music_name = escape_music_name.replace(',', '')
            escape_music_name = escape_music_name.replace('\n', '')
            escape_music_name = escape_music_name.replace('?', '')
            escape_music_name = escape_music_name.replace('!', '')
            escape_music_name = escape_music_name.replace('*', '')
            escape_music_name = escape_music_name.replace(':', '')

            print(music)
            for key in originals[music].keys():
                output_name = f'{escape_music_name}_{key}'

                for index in range(len(np_values[key])):
                    output_image = Image.fromarray(np_values[key][index])
                    output_image = output_image.convert('L')
                    output_filepath = join(music_inspection_basepath, f'{output_name}_{index}.png')
                    output_image.save(output_filepath)
                
                print(key, [(f'{target[:2]}', target[2:]) for target in map_keys[key][:6]])

    print(f'music count: {len(originals)}')

    return sorted([*originals.keys()]), mask, result

def organize_musics(keys, labels):
    difficulties = {}
    for difficulty in define.value_list['difficulties']:
        difficulties[difficulty] = []
    levels = {}
    for level in define.value_list['levels']:
        levels[level] = []

    for key in keys:
        target = labels[key]
        if not 'informations' in target.keys() or target['informations'] is None:
            continue

        informations = target['informations']
        if not 'music' in informations.keys() or informations['music'] is None:
            continue

        music = informations['music']
        if 'difficulty' in informations.keys() and informations['difficulty'] in define.value_list['difficulties']:
            difficulty = informations['difficulty']
            if not music in difficulties[difficulty]:
                difficulties[difficulty].append(music)
        if 'level' in informations.keys() and informations['level'] in define.value_list['levels']:
            level = informations['level']
            if not music in levels[level]:
                levels[level].append(music)
    
    for key, value in difficulties.items():
        print(key, len(value))
    for key, value in levels.items():
        print(key, len(value))

    return difficulties, levels

def check(target, arcade_all_musics, infinitas_only_musics):
    if type(target) is dict:
        for value in target.values():
            check(value, arcade_all_musics, infinitas_only_musics)
    else:
        if target is not None and not target in arcade_all_musics and not target in infinitas_only_musics:
            print(f"not found: {target}({target.encode('unicode-escape').decode()})")

def check_musics(musics, recog_musics):
    with open(arcadeallmusics_filename, 'r', encoding='utf-8') as f:
        arcade_all_musics = f.read().split('\n')

    with open(infinitasonlymusics_filename, 'r', encoding='utf-8') as f:
        infinitas_only_musics = f.read().split('\n')

    print(f'arcade all music count: : {len(arcade_all_musics)}')
    print(f'infinitas only music count: : {len(infinitas_only_musics)}')

    duplicates = list(set(arcade_all_musics) & set(infinitas_only_musics))
    if len(duplicates) > 0:
        print(f"duplicates: {','.join(duplicates)}")

    check(recog_musics, arcade_all_musics, infinitas_only_musics)

    return sorted([music for music in arcade_all_musics if not music in musics])

if __name__ == '__main__':
    recog_define = load_recognition_define()
    if recog_define is None:
        print(f"曲名認識定義ファイルのロードに失敗しました。")
        exit()
    
    if not isfile(dc.label_filepath):
        print(f"{dc.label_filepath}が見つかりませんでした。")
        exit()

    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        exit()
    
    ignore_keys_filepath = join(dc.collection_basepath, background_ignore_keys_filename)
    if isfile(ignore_keys_filepath):
        with open(ignore_keys_filepath, 'r', encoding='utf-8') as f:
            ignore_keys = f.read().split('\n')
    else:
        ignore_keys = []

    ignore_keys_filepath = join(dc.collection_basepath, background_ignore_keys_filename)
    if isfile(ignore_keys_filepath):
        with open(ignore_keys_filepath, 'r', encoding='utf-8') as f:
            ignore_keys = f.read().split('\n')
    else:
        ignore_keys = []
    
    create_resource_directory()

    output = []

    keys = [key for key in labels.keys() if labels[key]['informations'] is not None and labels[key]['informations']['music'] != '']
    print(f"file count: {len(keys)}")

    difficulties, levels = organize_musics(keys, labels)

    images = load_images(recog_define, keys, labels)

    area = recog_define['trimarea']
    shape = (area[3] - area[1], area[2] - area[0])

    backgrounds = generate_backgrounds(shape, images, ignore_keys)

    start = time.time()
    musics, mask, recog_musics = larning(recog_define, images, backgrounds)
    print(f'time: {time.time() - start}')

    missing_musics = check_musics(musics, recog_musics)

    for background_key in backgrounds.keys():
        backgrounds[background_key] = backgrounds[background_key].tolist()

    output = {
        'define': {
            'trimarea': recog_define['trimarea'],
            'background_key_position': recog_define['background_key_position'],
            'gray_thresholds': recog_define['gray_thresholds']
        },
        'backgrounds': backgrounds,
        'mask': mask.tolist(),
        'recognition': recog_musics,
        'musics': musics
    }

    with open(recog_musics_filepath, 'w') as f:
        json.dump(output, f)

    for music in musics:
        encoded = music.encode('UTF-8').hex()
        if len(encoded) > 240:
            print(f'Record file name too long: {music}')

    with open(registered_musics_filename, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(musics))

    with open(missing_musics_filename, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(missing_musics))
