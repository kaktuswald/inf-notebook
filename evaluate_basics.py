from PIL import Image
import json
import sys
import os
import pyautogui as pgui
from PIL import Image

from define import define
from resources import find_images
from recog import Recognition
from larning import raws_basepath,label_basics_filepath

result_filepath = 'evaluate_basics.csv'

failure = False

def evaluate(filename, image, label):
    global failure

    results = [filename]

    if not 'screen' in label.keys():
        results.append('none')
    else:
        screen_results = []
        for key in define.screen_areas.keys():
            if pgui.locate(find_images[key], image, grayscale=True) is not None:
                screen_results.append(key)
        if len(screen_results) == 1 and screen_results[0] == label['screen']:
            results.append('ok')
        else:
            results.append(','.join(screen_results))
            failure = True
    
    targets = {
        'loading': recog.search_loading,
        'music_select': recog.search_music_select,
        'result': recog.search_result
    }
    for key, value in targets.items():
        if not 'screen' in label.keys():
            results.append('none')
        else:
            if label['screen'] != key:
                results.append('')
            else:
                if value(image):
                    results.append('ok')
                else:
                    results.append('ng')
                    failure = True
    
    if not 'screen' in label.keys() or label['screen'] != 'result':
        results.append('not result')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('!')
        return results

    results.append('')

    targets = {
        'trigger': recog.search_trigger,
        'cutin_mission': recog.search_cutin_mission,
        'cutin_bit': recog.search_cutin_bit,
        'rival': recog.search_rival
    }
    for key, value in targets.items():
        if not key in label.keys():
            results.append('none')
        else:
            trigger = value(image)
            if trigger == label[key]:
                results.append('ok')
            else:
                results.append(f"{trigger} {label[key]}")
                failure = True

    if not 'play_side' in label.keys() or not 'cutin_mission' in label.keys() or label['cutin_mission']:
        results.append('none')
        play_side = None
    else:
        play_side = recog.get_play_side(image)
        if (play_side is None and label['play_side'] == '') or play_side == label['play_side']:
            results.append('ok')
        else:
            results.append(f"{play_side} {label['play_side']}")
            failure = True

    results.append('!')

    return results

if __name__ == '__main__':
    if not os.path.isfile(label_basics_filepath):
        print(f"{label_basics_filepath}が見つかりませんでした。")
        sys.exit()

    try:
        with open(label_basics_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{label_basics_filepath}を読み込めませんでした。")
        sys.exit()

    recog = Recognition()

    output = []

    filenames = [*labels.keys()]
    print(f"file count: {len(filenames)}")

    headers = [
        'screen',
        'loading',
        'music_select',
        'result',
        '',
        'trigger',
        'cutin_mission',
        'cutin_bit',
        'rival',
        'play_side',
        'result'
    ]

    output.append(f"file name,{','.join(headers)}\n")
    for filename in filenames:
        filepath = os.path.join(raws_basepath, filename)
        if not os.path.isfile(filepath):
            continue

        image = Image.open(filepath).convert('L')

        label = labels[filename]

        results = evaluate(filename, image, label)

        output.append(f"{','.join(results)}\n")

    output.append(f'result, {not failure}')
    print(not failure)
    
    with open(result_filepath, 'w') as f:
        f.writelines(output)
        f.close()
