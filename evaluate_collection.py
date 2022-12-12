from PIL import Image
import json
import sys
import os

from define import value_list
from recog import Recognition
import data_collection as dc

result_filepath = 'evaluate_collection.csv'

failure = False

def evaluate(filename, informations, details, label):
    global failure

    results = [filename]
    
    if informations is not None:
        play_mode, difficulty, level, music = recog.get_informations(informations)

        if not 'play_mode' in label.keys():
            results.append('none')
        else:
            if play_mode == label['play_mode']:
                results.append('ok')
            else:
                results.append(f"{play_mode} {label['play_mode']}")
                failure = True

        if not 'difficulty' in label.keys() or not 'level' in label.keys():
            results.append('none')
            results.append('none')
        else:
            if difficulty == label['difficulty']:
                results.append('ok')
            else:
                results.append(f"{difficulty} {label['difficulty']}")
                failure = True

            if level == label['level']:
                results.append('ok')
            else:
                results.append(f"{level} {label['level']}")
                failure = True

        if not 'music' in label.keys():
            results.append('none')
        else:
            results.append('')
            # if play_mode == label['music']:
            #     results.append('ok')
            # else:
            #     results.append(f"{music} {label['music']}")
            #     failure = True
    else:
        results.append('')
        results.append('')
        results.append('')
        results.append('')

    if details is not None:
        option, clear_type, dj_level, score, miss_count, clear_type_new, dj_level_new, score_new, miss_count_new = recog.get_details(details)

        if option is None:
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
        else:
            if not 'option_arrange' in label.keys():
                results.append('none')
            else:
                if option['arrange'] in value_list['options_arrange']:
                    if option['arrange'] == label['option_arrange']:
                        results.append('ok')
                    else:
                        results.append(f"{option['arrange']} {label['option_arrange']}")
                        failure = True
                else:
                    results.append('ok')
            
            if not 'option_arrange_dp' in label.keys():
                results.append('none')
            else:
                if option['arrange'] is not None and '/' in option['arrange']:
                    if option['arrange'] == label['option_arrange_dp']:
                        results.append('ok')
                    else:
                        results.append(f"{option['arrange']} {label['option_arrange_dp']}")
                        failure = True
                else:
                    results.append('ok')
            
            if not 'option_arrange_sync' in label.keys():
                results.append('none')
            else:
                if option['arrange'] in value_list['options_arrange_sync']:
                    if option['arrange'] == label['option_arrange_sync']:
                        results.append('ok')
                    else:
                        results.append(f"{option['arrange']} {label['option_arrange_sync']}")
                        failure = True
                else:
                    results.append('ok')
            
            if not 'option_flip' in label.keys():
                results.append('none')
            else:
                if (option['flip'] is None and label['option_flip'] == '') or option['flip'] == label['option_flip']:
                    results.append('ok')
                else:
                    results.append(f"{option['flip']} {label['option_flip']}")
                    failure = True
            
            if not 'option_assist' in label.keys():
                results.append('none')
            else:
                if (option['assist'] is None and label['option_assist'] == '') or option['assist'] == label['option_assist']:
                    results.append('ok')
                else:
                    results.append(f"{option['assist']} {label['option_assist']}")
                    failure = True
            
            if not 'option_battle' in label.keys():
                results.append('none')
            else:
                if (option['battle'] is None and label['option_battle'] == '') or option['battle'] == label['option_battle']:
                    results.append('ok')
                else:
                    results.append(f"{option['battle']} {label['option_battle']}")
                    failure = True
            
            if not 'option_h-random' in label.keys():
                results.append('none')
            else:
                if (option['h-random'] is None and label['option_h-random'] == '') or option['h-random'] == label['option_h-random']:
                    results.append('ok')
                else:
                    results.append(f"{option['h-random']} {label['option_h-random']}")
                    failure = True

        if not 'clear_type' in label.keys():
            results.append('none')
        else:
            if (clear_type is None and label['clear_type'] == '') or clear_type == label['clear_type']:
                results.append('ok')
            else:
                results.append(f"{clear_type} {label['clear_type']}")
                failure = True

        if not 'dj_level' in label.keys():
            results.append('none')
        else:
            if (dj_level is None and label['dj_level'] == '') or dj_level == label['dj_level']:
                results.append('ok')
            else:
                results.append(f"{dj_level} {label['dj_level']}")

        if not 'score' in label.keys():
            results.append('none')
        else:
            if (score is None and label['score'] == '') or score == int(label['score']):
                results.append('ok')
            else:
                results.append(f"{score} {label['score']}")

        if not 'miss_count' in label.keys():
            results.append('none')
        else:
            if (miss_count is None and label['miss_count'] == '') or miss_count == int(label['miss_count']):
                results.append('ok')
            else:
                results.append(f"{miss_count} {label['miss_count']}")

        if not 'clear_type_new' in label.keys():
            results.append('none')
        else:
            if clear_type_new == label['clear_type_new']:
                results.append('ok')
            else:
                results.append(f"{clear_type_new} {label['clear_type_new']}")
        
        if not 'dj_level_new' in label.keys():
            results.append('none')
        else:
            if dj_level_new == label['dj_level_new']:
                results.append('ok')
            else:
                results.append(f"{dj_level_new} {label['dj_level_new']}")
        
        if not 'score_new' in label.keys():
            results.append('none')
        else:
            if score_new == label['score_new']:
                results.append('ok')
            else:
                results.append(f"{score_new} {label['score_new']}")
        
        if not 'miss_count_new' in label.keys():
            results.append('none')
        else:
            if miss_count_new == label['miss_count_new']:
                results.append('ok')
            else:
                results.append(f"{miss_count_new} {label['miss_count_new']}")
    else:
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')
    
    results.append('!')

    return results

if __name__ == '__main__':
    if not os.path.isfile(dc.label_filepath):
        print(f"{dc.label_filepath}が見つかりませんでした。")
        sys.exit()

    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        sys.exit()

    recog = Recognition()

    output = []

    keys = [*labels.keys()]
    print(f"file count: {len(keys)}")

    headers = [
        'play_mode',
        'difficulty',
        'level',
        'music',
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
    for key in keys:
        filename = f'{key}.png'

        informations_image = None
        details_image = None
        informations_filepath = os.path.join(dc.informations_basepath, filename)
        if os.path.isfile(informations_filepath):
            informations_image = Image.open(informations_filepath).convert('L')
        details_filepath = os.path.join(dc.details_basepath, filename)
        if os.path.isfile(details_filepath):
            details_image = Image.open(details_filepath).convert('L')

        if informations_image is None and details_image is None:
            continue

        label = labels[key]

        results = evaluate(filename, informations_image, details_image, label)

        output.append(f"{','.join(results)}\n")
    
    output.append(f'result, {not failure}')
    print(not failure)
    
    with open(result_filepath, 'w') as f:
        f.writelines(output)
        f.close()
