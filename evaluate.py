from PIL import Image
import json
import sys
import os

from define import value_list
from recog import Recognition
from larning import raws_basepath

labels_filepath = os.path.join(raws_basepath, 'label.json')
result_filepath = 'evaluate.csv'

keys_number = ['score', 'miss_count']
keys_new = ['clear_type_new', 'dj_level_new', 'score_new', 'miss_count_new']

def evaluate(filename, image, label):
    results = [filename]
    
    if not 'starting' in label.keys():
        results.append('none')
    else:
        starting = recog.get_starting(image)
        if starting is not None and label['starting'] == '':
            return ''
        else:
            results.append('' if starting == label['starting'] else f"{starting} {label['starting']}")
        if not starting is None:
            return results

    trigger = recog.search_trigger(image)
    results.append('' if trigger == label['trigger'] else f"{trigger} {label['trigger']}")

    cutin_mission = recog.search_cutin_mission(image)
    results.append('' if cutin_mission == label['cutin_mission'] else f"{cutin_mission} {label['cutin_mission']}")

    cutin_bit = recog.search_cutin_bit(image)
    results.append('' if cutin_bit == label['cutin_bit'] else f"{cutin_bit} {label['cutin_bit']}")

    if not trigger or cutin_mission or cutin_bit:
        results.append('not result')
        return results
    
    play_side = None
    if not 'play_side' in label.keys():
        results.append('none')
    else:
        play_side = recog.get_play_side(image)
        results.append('' if play_side == label['play_side'] else f"{play_side} {label['play_side']}")

    if play_side is None:
        results.append('no play side')
        return results

    if not 'rival' in label.keys():
        results.append('none')
    else:
        result = recog.search_rival(image)
        results.append('' if result == label['rival'] else f"{result} {label['rival']}")

    play_mode = None
    if not 'play_mode' in label.keys():
        results.append('not play_mode')
    else:
        play_mode = recog.get_play_mode(image)
        results.append('' if play_mode == label['play_mode'] else f"{result} {label['play_mode']}")

    if play_mode is None:
        results.append('no play mode')
        return results

    if not 'difficulty' in label.keys() or not 'level' in label.keys():
        results.append('none')
        results.append('none')
    else:
        difficulty, level = recog.get_level(image)
        results.append('' if difficulty == label['difficulty'] else f"{difficulty} {label['difficulty']}")
        results.append('' if level == label['level'] else f"{level} {label['dilevelfficulty']}")

    if not 'use_option' in label.keys():
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
    else:
        option = recog.get_option(play_side, image)
        if (option is None and not label['use_option']) or (option is not None and label['use_option']):
            results.append('')
        else:
            results.append(f"{option is not None} {label['use_option']}")
        
        if not option is None:
            if not 'option_arrange' in label.keys():
                results.append('none')
            else:
                if option['arrange'] in value_list['options_arrange']:
                    results.append('' if option['arrange'] == label['option_arrange'] else f"{option['arrange']} {label['option_arrange']}")
                else:
                    results.append('')
            if not 'option_arrange_dp' in label.keys():
                results.append('none')
            else:
                if option['arrange'] is not None and '/' in option['arrange']:
                    results.append('' if option['arrange'] == label['option_arrange_dp'] else f"{option['arrange']} {label['option_arrange_dp']}")
                else:
                    results.append('')
            if not 'option_arrange_sync' in label.keys():
                results.append('none')
            else:
                if option['arrange'] in value_list['options_arrange_sync']:
                    results.append('' if option['arrange'] == label['option_arrange_sync'] else f"{option['arrange']} {label['option_arrange_sync']}")
                else:
                    results.append('')
            if not 'option_flip' in label.keys():
                results.append('none')
            else:
                results.append('' if option['flip'] == label['option_flip'] else f"{option['flip']} {label['option_flip']}")
            if not 'option_assist' in label.keys():
                results.append('none')
            else:
                results.append('' if option['assist'] == label['option_assist'] else f"{option['assist']} {label['option_assist']}")
            if not 'option_battle' in label.keys():
                results.append('none')
            else:
                results.append('' if option['battle'] == label['option_battle'] else f"{option['battle']} {label['option_battle']}")
            if not 'option_h-random' in label.keys():
                results.append('none')
            else:
                results.append('' if option['h-random'] == label['option_h-random'] else f"{option['h-random']} {label['option_h-random']}")
        else:
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')


    if not 'clear_type' in label.keys():
        results.append('none')
    else:
        result = recog.get_clear_type(play_side, image)
        results.append('' if result == '' or result == label['clear_type'] else f"{result} {label['clear_type']}")

    if not 'dj_level' in label.keys():
        results.append('none')
    else:
        result = recog.get_dj_level(play_side, image)
        results.append('' if result == label['dj_level'] else f"{result} {label['dj_level']}")

    for key in keys_number:
        if not key in label.keys():
            results.append('none')
        else:
            if label[key].isnumeric():
                result = recog.get_number(play_side, key, image)
                results.append('' if result == int(label[key]) else f"{result} {label[key]}")
            else:
                results.append('')

    for key in keys_new:
        if not key in label.keys():
            results.append('none')
        else:
            result = recog.is_new(play_side, key, image)
            results.append('' if result == label[key] else f'{result} {label[key]}')
    
    results.append('OK!')

    return results

if __name__ == '__main__':
    if not os.path.isfile(labels_filepath):
        print(f"{labels_filepath}が見つかりませんでした。")
        sys.exit()

    try:
        with open(labels_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{labels_filepath}を読み込めませんでした。")
        sys.exit()

    recog = Recognition()

    output = []

    filenames = [*labels.keys()]
    print(f"file count: {len(filenames)}")

    headers = [
        'starting',
        'trigger',
        'cutin_mission',
        'cutin_bit',
        'play_side',
        'rival',
        'play_mode',
        'difficulty',
        'level',
        'use_option',
        'option_arrange',
        'option_arrange_dp',
        'option_arrange_sync',
        'option_flip',
        'option_assist',
        'option_battle',
        'option_h-random',
        'clear_type',
        'dj_level',
        'score',
        'miss_count',
        'clear_type_new',
        'dj_level_new',
        'score_new',
        'miss_count_new',
        'result'
    ]

    output.append(f"ファイル名,{','.join(headers)}\n")
    for filename in filenames:
        filepath = os.path.join(raws_basepath, filename)
        if not os.path.isfile(filepath):
            continue

        image = Image.open(filepath).convert('L')

        label = labels[filename]

        results = evaluate(filename, image, label)

        output.append(f"{','.join(results)}\n")
    
    with open(result_filepath, 'w') as f:
        f.writelines(output)
        f.close()
