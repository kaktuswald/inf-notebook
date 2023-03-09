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

dirname = 'larning_music'

if not exists(dirname):
    mkdir(dirname)

music_inspection_basepath = join(dirname, 'inspection')

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'
registred_musics_filename = 'musics_registred.txt'
missing_musics_filename = 'musics_missing_in_arcade.txt'

area = define.informations_areas['music']
width = area[2] - area[0]
height = area[3] - area[1]
shape = (height, width)

class InformationsImage():
    def __init__(self, filepath, music):
        image = Image.open(filepath)
        self.background_key = image.getpixel(define.music_background_key_position)
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
    
def generate_backgrounds(images):
    background_sources = {}
    for image in images.values():
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
    for key, image in images.items():
        if not image.music in musics.keys():
            musics[image.music] = {}
        musics[image.music][key] = image

    inspect_targets = []

    np_values = {}
    binary_values = {}
    map = {}
    report = {}
    is_ok = True

    for music in musics.keys():
        report[music] = {}

        for key, image in musics[music].items():
            np_values[key] = []
            binary_values[key] = []

            background_key = image.background_key
            np_value = image.np_value
            np_values[key].append(np_value)

            background_removed = np.where(backgrounds[background_key]!=np_value, np_value, 0)
            np_values[key].append(background_removed)

            trimmed = np.delete(background_removed, define.music_ignore_y_lines, 0)
            np_values[key].append(trimmed)

            maxcounts = []
            maxcount_values = []
            for line in trimmed:
                unique, counts = np.unique(line, return_counts=True)
                dark_count = np.count_nonzero(unique < 100)
                maxcounts.append(counts[np.argmax(counts[dark_count:])+dark_count] if len(counts) > dark_count else 0)
                maxcount_values.append(unique[np.argmax(counts[dark_count:])+dark_count] if len(unique) > dark_count else 0)

            y = np.argmax(maxcounts)
            color = int(maxcount_values[y])

            mask = np.zeros(trimmed.shape)
            mask[np.argmax(maxcounts),:] = maxcount_values[y]
            result = np.where(trimmed==mask,trimmed,0)
            np_values[key].append(result)

            y_key = str(y)
            if not y_key in map.keys():
                map[y_key] = {}
            target = map[y_key]

            color_key = str(color)
            if not color_key in target.keys():
                target[color_key] = {}
            target = target[color_key]

            line = np.where(trimmed[y]==color, 1, 0)
            line_key = str(int(''.join(line.astype(str)), 2))
            if type(line_key) is not str:
                print(line_key)

            if line_key in target.keys() and target[line_key] != music:
                print('duplicate', music, target[line_key], key)
                inspect_targets.append(music)
                inspect_targets.append(target[line_key])
                is_ok = False

            target[line_key] = music

            report[music][key] = sum(result)

    for music in [*report.keys()]:
        count = len(np.unique(np.array([np.sum(np_value) for np_value in report[music].values()])))
        if len(inspect_targets) < 2 and count != 1:
            print('not unique', music, count, [f'{key}: {np.sum(item)}' for key, item in report[music].items()])
            inspect_targets.append(music)
    
    if len(inspect_targets) > 0:
        for filepath in glob(join(music_inspection_basepath, '*.png')):
            try:
                remove(filepath)
            except Exception as ex:
                print(ex)

        for background_key in backgrounds.keys():
            output_image = Image.fromarray(backgrounds[background_key])
            output_filepath = join(music_inspection_basepath, f'background_{background_key}.png')
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

    if is_ok:
        print('larning OK!')

    return [*musics.keys()], map if is_ok else None

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

    create_resource_directory()

    output = []

    keys = [key for key in labels.keys() if labels[key]['informations'] is not None and labels[key]['informations']['music'] != '']
    print(f"file count: {len(keys)}")

    images = load_images(keys, labels)

    backgrounds = generate_backgrounds(images)

    start = time.time()
    musics, recog_musics = larning(images, backgrounds)
    print(f'time: {time.time() - start}')

    missing_musics = check_musics(musics, recog_musics)

    for background_key in backgrounds.keys():
        backgrounds[background_key] = backgrounds[background_key].tolist()

    output = {
        'backgrounds': backgrounds,
        'recognition': recog_musics
    }

    with open(recog_musics_filepath, 'w') as f:
        json.dump(output, f)

    with open(registred_musics_filename, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(musics))

    with open(missing_musics_filename, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(missing_musics))

