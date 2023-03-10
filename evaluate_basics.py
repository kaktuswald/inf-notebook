from PIL import Image
import json
import sys
import os
from PIL import Image

from recog import Recognition
from larning import raws_basepath,label_basics_filepath

result_filepath = 'evaluate_basics.csv'

def evaluate(filename, image, label):
    failure = False
    results = [filename]

    if image.size == (1280, 720):
        results.append('ok')
    else:
        results.append(image.size)
        if not 'screen' in label.keys() or label['screen'] != '':
            failure = True
        return results, failure
    
    screen_keys = ('loading', 'music_select', 'playing', 'result',)
    screen_results = {
        'loading': recog.get_is_screen_loading(image),
        'music_select': recog.get_is_screen_music_select(image),
        'playing': recog.get_is_screen_playing(image),
        'result': recog.get_is_screen_result(image)
    }
    for key in screen_keys:
        if not 'screen' in label.keys() or label['screen'] != key:
            results.append('none')
        else:
            if screen_results[key] and label['screen'] == key:
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
        results.append('')
        results.append('')
        results.append('ok' if not failure else 'NG')
        return failure, results

    results.append('')

    targets = {
        'trigger': recog.get_has_trigger,
        'cutin_mission': recog.get_has_cutin_mission,
        'cutin_bit': recog.get_has_cutin_bit,
        'rival': recog.get_has_rival
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

    if not 'play_side' in label.keys() or not 'dead' in label.keys() or not 'cutin_mission' in label.keys() or label['cutin_mission']:
        results.append('none')
        play_side = None
    else:
        dead = recog.get_has_dead(image, label['play_side'])
        if (dead is None and label['dead'] == '') or dead == label['dead']:
            results.append('ok')
        else:
            results.append(f"{dead} {label['dead']}")
            failure = True

    results.append('ok' if not failure else 'NG')

    return failure, results

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
        'size',
        'loading',
        'music_select',
        'playing',
        'result',
        '',
        'trigger',
        'cutin_mission',
        'cutin_bit',
        'rival',
        'play_side',
        'dead',
        'result'
    ]

    result_failure = False
    output.append(f"file name,{','.join(headers)}\n")
    for filename in filenames:
        filepath = os.path.join(raws_basepath, filename)
        if not os.path.isfile(filepath):
            continue

        image = Image.open(filepath).convert('L')

        label = labels[filename]

        failure, results = evaluate(filename, image, label)
        if failure:
            result_failure = failure

        output.append(f"{','.join(results)}\n")

    output.append(f'result, {not result_failure}')
    print(not result_failure)
    
    with open(result_filepath, 'w') as f:
        f.writelines(output)
        f.close()
