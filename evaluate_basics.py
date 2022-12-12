from PIL import Image
import json
import sys
import os

from recog import Recognition
from larning import raws_basepath,label_basics_filepath

result_filepath = 'evaluate_basics.csv'

failure = False

def evaluate(filename, image, label):
    global failure

    results = [filename]
    
    starting = recog.get_starting(image)
    if starting is not None:
        if not 'startinig' in label.keys() or starting == label['starting']:
            results.append('ok')
        else:
            results.append(f"{starting} {label['starting']}")
            failure = True

        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('!')
        return results

    results.append('ok')

    if not 'trigger' in label.keys():
        results.append('none')
    else:
        trigger = recog.search_trigger(image)
        if trigger == label['trigger']:
            results.append('ok')
        else:
            results.append(f"{trigger} {label['trigger']}")
            failure = True

    if not 'cutin_mission' in label.keys():
        results.append('none')
    else:
        cutin_mission = recog.search_cutin_mission(image)
        if cutin_mission == label['cutin_mission']:
            results.append('ok')
        else:
            results.append(f"{cutin_mission} {label['cutin_mission']}")
            failure = True

    if not 'cutin_bit' in label.keys():
        results.append('none')
    else:
        cutin_bit = recog.search_cutin_bit(image)
        if cutin_bit == label['cutin_bit']:
            results.append('ok')
        else:
            results.append(f"{cutin_bit} {label['cutin_bit']}")
            failure = True

    if not trigger or cutin_mission or cutin_bit:
        results.append('not result')
        results.append('')
        results.append('')
        results.append('!')
        return results
    
    results.append('')

    if not 'play_side' in label.keys():
        results.append('none')
        play_side = None
    else:
        play_side = recog.get_play_side(image)
        if (play_side is None and label['play_side'] == '') or play_side == label['play_side']:
            results.append('ok')
        else:
            results.append(f"{play_side} {label['play_side']}")
            failure = True

    if not 'rival' in label.keys():
        results.append('none')
    else:
        result = recog.search_rival(image)
        if result == label['rival']:
            results.append('ok')
        else:
            results.append(f"{result} {label['rival']}")
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
        'starting',
        'trigger',
        'cutin_mission',
        'cutin_bit',
        '',
        'play_side',
        'rival',
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

    output.append(f'result, {not failure}')
    print(not failure)
    
    with open(result_filepath, 'w') as f:
        f.writelines(output)
        f.close()
