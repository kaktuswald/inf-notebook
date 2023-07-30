from PIL import Image
import json
from sys import exit
from os.path import join,isfile
import numpy as np

from define import define
import data_collection as dc

class Informations():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_informations(labels):
    keys = [key for key in labels.keys() if labels[key]['informations'] is not None]

    informations = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if isfile(filepath):
            image = Image.open(filepath)
            if image.height != 78:
                continue

            np_value = np.array(image)
            informations[key] = Informations(np_value, labels[key]['informations'])
    
    return informations

def analyze(informations):
    print(f'Count: {len(informations)}')

    table = {}
    for key, target in informations.items():
        if not 'play_mode' in target.label.keys() or target.label['play_mode'] is None:
            continue
        if not 'difficulty' in target.label.keys() or target.label['difficulty'] is None:
            continue
        if not 'level' in target.label.keys() or target.label['level'] is None:
            continue
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue
        if not 'notes' in target.label.keys() or target.label['notes'] is None:
            continue
        
        play_mode = target.label['play_mode']
        difficulty = target.label['difficulty']
        level = target.label['level']
        music = target.label['music']

        if not music in table.keys():
            table[music] = {}
            for pm in define.value_list['play_modes']:
                table[music][pm] = {}
                for df in define.value_list['difficulties']:
                    table[music][pm][df] = {}
        
        if not level in table[music][play_mode][difficulty].values():
            table[music][play_mode][difficulty][key] = level
    
    output = []
    errors = []
    for music in table.keys():
        values = [music]
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                if len(table[music][play_mode][difficulty]) > 1 and play_mode == 'DP':
                    if len(table[music]['SP'][difficulty]) == 1:
                        for key, value in table[music][play_mode][difficulty].items():
                            if value == table[music]['SP'][difficulty].values()[0]:
                                del table[music][play_mode][difficulty][key]
                values.append([*table[music][play_mode][difficulty].values()][0] if len(table[music][play_mode][difficulty]) == 1 else '-')
                if len(table[music][play_mode][difficulty]) > 1:
                    errors.append(f'{music} {play_mode} {difficulty}:')
                    for key, value in table[music][play_mode][difficulty].items():
                        errors.append(f'  level {value}({key})')
        output.append(','.join(values))

    with open('musics_analyzed.csv', 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))
    
    if len(errors) > 0:
        print(f'There was an error.')
        erros_filepath = join('report', 'musics_analyzed_errors.txt')
        with open(erros_filepath, 'w', encoding='UTF-8') as f:
            f.write('\n'.join(errors))

if __name__ == '__main__':
    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        exit()
    
    informations = load_informations(labels)
    
    analyze(informations)
