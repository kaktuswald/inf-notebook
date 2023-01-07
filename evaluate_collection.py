from PIL import Image
import json
import sys
import os

from define import define
from recog import Recognition
import data_collection as dc

result_filepath = 'evaluate_collection.csv'

failure = False

def evaluate(filename, informations, details, label):
    global failure

    results = [filename]
    
    if informations is not None:
        recog_informations = recog.get_informations(informations)

        if not 'play_mode' in label.keys():
            results.append('none')
        else:
            if recog_informations.play_mode == label['play_mode']:
                results.append('ok')
            else:
                results.append(f"{recog_informations.play_mode} {label['play_mode']}")
                failure = True

        if not 'difficulty' in label.keys() or not 'level' in label.keys():
            results.append('none')
            results.append('none')
        else:
            if recog_informations.difficulty == label['difficulty']:
                results.append('ok')
            else:
                results.append(f"{recog_informations.difficulty} {label['difficulty']}")
                failure = True

            if recog_informations.level == label['level']:
                results.append('ok')
            else:
                results.append(f"{recog_informations.level} {label['level']}")
                failure = True

        if not 'music' in label.keys() or label['music'] == '':
            results.append('none')
        else:
            if recog_informations.music == label['music']:
                results.append('ok')
            else:
                results.append(f"{recog_informations.music} {label['music']}")
                failure = True
    else:
        results.append('')
        results.append('')
        results.append('')
        results.append('')

    if details is not None:
        recog_details = recog.get_details(details)

        recog_options = recog_details.options
        if recog_options is None:
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
                if recog_options.arrange in define.value_list['options_arrange']:
                    if recog_options.arrange == label['option_arrange']:
                        results.append('ok')
                    else:
                        results.append(f"{recog_options.arrange} {label['option_arrange']}")
                        failure = True
                else:
                    results.append('ok')
            
            if not 'option_arrange_dp' in label.keys():
                results.append('none')
            else:
                if recog_options.arrange is not None and '/' in recog_options.arrange:
                    if recog_options.arrange == label['option_arrange_dp']:
                        results.append('ok')
                    else:
                        results.append(f"{recog_options.arrange} {label['option_arrange_dp']}")
                        failure = True
                else:
                    results.append('ok')
            
            if not 'option_arrange_sync' in label.keys():
                results.append('none')
            else:
                if recog_options.arrange in define.value_list['options_arrange_sync']:
                    if recog_options.arrange == label['option_arrange_sync']:
                        results.append('ok')
                    else:
                        results.append(f"{recog_options.arrange} {label['option_arrange_sync']}")
                        failure = True
                else:
                    results.append('ok')
            
            if not 'option_flip' in label.keys():
                results.append('none')
            else:
                if (recog_options.flip is None and label['option_flip'] == '') or recog_options.flip == label['option_flip']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.flip} {label['option_flip']}")
                    failure = True
            
            if not 'option_assist' in label.keys():
                results.append('none')
            else:
                if (recog_options.assist is None and label['option_assist'] == '') or recog_options.assist == label['option_assist']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.assist} {label['option_assist']}")
                    failure = True
            
            if not 'option_battle' in label.keys():
                results.append('none')
            else:
                if (recog_options.battle is None and label['option_battle'] == '') or recog_options.battle == label['option_battle']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.battle} {label['option_battle']}")
                    failure = True
            
            if not 'option_h-random' in label.keys():
                results.append('none')
            else:
                if (recog_options.h_random is None and label['option_h-random'] == '') or recog_options.h_random == label['option_h-random']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.h_random} {label['option_h-random']}")
                    failure = True

        recog_clear_type = recog_details.clear_type
        recog_dj_level = recog_details.dj_level
        recog_score = recog_details.score
        recog_miss_count = recog_details.miss_count

        if not 'clear_type' in label.keys():
            results.append('none')
        else:
            if (recog_clear_type.value is None and label['clear_type'] == '') or recog_clear_type.value == label['clear_type']:
                results.append('ok')
            else:
                results.append(f"{recog_clear_type.value} {label['clear_type']}")
                failure = True

        if not 'dj_level' in label.keys():
            results.append('none')
        else:
            if (recog_dj_level.value is None and label['dj_level'] == '') or recog_dj_level.value == label['dj_level']:
                results.append('ok')
            else:
                results.append(f"{recog_dj_level.value} {label['dj_level']}")

        if not 'score' in label.keys():
            results.append('none')
        else:
            if (recog_score.value is None and label['score'] == '') or recog_score.value == int(label['score']):
                results.append('ok')
            else:
                results.append(f"{recog_score.value} {label['score']}")

        if not 'miss_count' in label.keys():
            results.append('none')
        else:
            if (recog_miss_count.value is None and label['miss_count'] == '') or recog_miss_count.value == int(label['miss_count']):
                results.append('ok')
            else:
                results.append(f"{recog_miss_count.value} {label['miss_count']}")

        if not 'clear_type_new' in label.keys():
            results.append('none')
        else:
            if recog_clear_type.new == label['clear_type_new']:
                results.append('ok')
            else:
                results.append(f"{recog_clear_type.new} {label['clear_type_new']}")
        
        if not 'dj_level_new' in label.keys():
            results.append('none')
        else:
            if recog_dj_level.new == label['dj_level_new']:
                results.append('ok')
            else:
                results.append(f"{recog_dj_level.new} {label['dj_level_new']}")
        
        if not 'score_new' in label.keys():
            results.append('none')
        else:
            if recog_score.new == label['score_new']:
                results.append('ok')
            else:
                results.append(f"{recog_score.new} {label['score_new']}")
        
        if not 'miss_count_new' in label.keys():
            results.append('none')
        else:
            if recog_miss_count.new == label['miss_count_new']:
                results.append('ok')
            else:
                results.append(f"{recog_miss_count.new} {label['miss_count_new']}")
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

    output.append(f"file name,{','.join(headers)}\n")
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
    
    with open(result_filepath, 'w', encoding='utf-8') as f:
        f.writelines(output)
        f.close()
