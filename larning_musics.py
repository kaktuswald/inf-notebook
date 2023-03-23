from PIL import Image
import json
from sys import exit
from os import mkdir,remove
from os.path import join,isfile,exists
import numpy as np
from glob import glob
from scipy.stats import mode
import time

from resources import recog_musics_filepath
import data_collection as dc
from larning import create_resource_directory

class MusicRecognitionDefine():
    trimarea = (180, 0, 250, 12)
    background_key_position = (0, -2)
    ignore_y_lines = (1, 2, 4, 6, 7, )
    ignore_x_lines = (27, 29, 37, 38, 40, 55, 56, 62, )

music_define = MusicRecognitionDefine

background_ignore_keys_filename = 'background_ignore_keys.txt'
dirname = 'larning_music'

if not exists(dirname):
    mkdir(dirname)

music_inspection_basepath = join(dirname, 'inspection')

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'
registered_musics_filename = 'musics_registered.txt'
missing_musics_filename = 'musics_missing_in_arcade.txt'

area = music_define.trimarea
width = area[2] - area[0]
height = area[3] - area[1]
shape = (height, width)

class InformationsImage():
    def __init__(self, filepath, music):
        image = Image.open(filepath)
        self.background_key = image.getpixel(music_define.background_key_position)
        np_value = np.array(image)
        self.np_value = np_value[area[1]:area[3], area[0]:area[2]]
        self.music = music

def load_images(keys, labels):
    images = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if isfile(filepath):
            images[key] = InformationsImage(filepath, labels[key]['informations']['music'])
    
    return images
    
def generate_backgrounds(images, ignore_keys):
    background_sources = {}
    for key, image in images.items():
        if key in ignore_keys:
            continue
        if not image.background_key in background_sources.keys():
            background_sources[image.background_key] = []
        background_sources[image.background_key].append(image.np_value)

    print('background sources')
    backgrounds = {}
    for background_key in background_sources.keys():
        stacks = np.stack(background_sources[background_key])
        result, counts = mode(stacks, keepdims=True)
        result_background = result.reshape(shape)

        backgrounds[background_key] = result_background

        print(f'{background_key}: {len(background_sources[background_key])}')
    
    return backgrounds

def larning(images, backgrounds):
    musics = {}
    for key, image in [*images.items()]:
        if not image.music in musics.keys():
            musics[image.music] = {}
        musics[image.music][key] = image

    inspect_targets = []

    np_values = {}
    binary_values = {}
    map = {}
    unique_test = {}

    for music in musics.keys():
        for key, image in musics[music].items():
            np_values[key] = []
            binary_values[key] = []

            background_key = image.background_key
            np_value = image.np_value
            np_values[key].append(np_value)

            background_removed = np.where(backgrounds[background_key]!=np_value, np_value, 0)
            np_values[key].append(background_removed)

            y_trimmed = np.delete(background_removed, music_define.ignore_y_lines, 0)
            trimmed = np.delete(y_trimmed, music_define.ignore_x_lines, 1)
            np_values[key].append(trimmed)

            maxcounts = []
            maxcount_values = []
            for line in trimmed:
                unique, counts = np.unique(line, return_counts=True)
                dark_count = np.count_nonzero(unique < 100)
                maxcounts.append(counts[np.argmax(counts[dark_count:])+dark_count] if len(counts) > dark_count else 0)
                maxcount_values.append(unique[np.argmax(counts[dark_count:])+dark_count] if len(unique) > dark_count else 0)

            y = np.argmax(maxcounts)
            count = maxcounts[y]
            color = int(maxcount_values[y])
            key_first = f'{y:02}{count:02}{color:03}'
            if not music in unique_test.keys():
                unique_test[music] = []
            unique_test[music].append(key_first)

            mapkeys = []
            for y in np.argsort(maxcounts)[::-1]:
                count = maxcounts[y]
                color = int(maxcount_values[y])
                mapkeys.append(f'{y:02}{count:02}{color:03}')

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
    
    with open('unique_test.txt', 'w', encoding='UTF-8') as f:
        for key, value in unique_test.items():
            f.write(f'({len(set(value))}) {key}({len(value)}): {value}\n')
    
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

    for music, keys in [*report.items()]:
        if len(keys) >= 2 and len(inspect_targets) < 2:
            print('not unique', music, keys)
            inspect_targets.append(music)
    # inspect_targets.append('CaptivAte～裁き～')
    # inspect_targets.append('CaptivAte～誓い～')
    
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

            for key in musics[music].keys():
                output_name = f'{escape_music_name}_{key}'

                for index in range(len(np_values[key])):
                    output_image = Image.fromarray(np_values[key][index])
                    output_image = output_image.convert('L')
                    output_filepath = join(music_inspection_basepath, f'{output_name}_{index}.png')
                    output_image.save(output_filepath)

    print(f'music count: {len(musics)}')

    return [*musics.keys()], result

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

    return [music for music in arcade_all_musics if not music in musics]

if __name__ == '__main__':
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

    images = load_images(keys, labels)

    backgrounds = generate_backgrounds(images, ignore_keys)

    start = time.time()
    musics, recog_musics = larning(images, backgrounds)
    print(f'time: {time.time() - start}')

    missing_musics = check_musics(musics, recog_musics)

    for background_key in backgrounds.keys():
        backgrounds[background_key] = backgrounds[background_key].tolist()

    output = {
        'define': {
            'trimarea': music_define.trimarea,
            'background_key_position': music_define.background_key_position,
            'ignore_y_lines': music_define.ignore_y_lines,
            'ignore_x_lines': music_define.ignore_x_lines,
        },
        'backgrounds': backgrounds,
        'recognition': recog_musics
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
