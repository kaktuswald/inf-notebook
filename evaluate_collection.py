from PIL import Image
import json
import sys
import os

from define import define
from recog import Recognition
import data_collection as dc

result_filepath = 'evaluate_collection.csv'

failure = False

def evaluate(filename, informations, details, key, label):
    global failure

    results = [filename]
    
    if label['informations'] is not None and informations is not None:
        recog_informations = recog.get_informations(informations)

        if recog_informations.play_mode == label['informations']['play_mode']:
            results.append('ok')
        else:
            results.append(f"{recog_informations.play_mode} {label['informations']['play_mode']}")
            failure = True

        if recog_informations.difficulty == label['informations']['difficulty']:
            results.append('ok')
        else:
            results.append(f"{recog_informations.difficulty} {label['informations']['difficulty']}")
            failure = True

        if recog_informations.level == label['informations']['level']:
            results.append('ok')
        else:
            results.append(f"{recog_informations.level} {label['informations']['level']}")
            failure = True

        if 'notes' in label['informations'].keys():
            if recog_informations.level == label['informations']['level']:
                results.append('ok')
            else:
                results.append(f"{recog_informations.notes} {label['informations']['notes']}")
                failure = True
        else:
            results.append('??')


        if recog_informations.music == label['informations']['music']:
            results.append('ok')
        else:
            results.append(f"{recog_informations.music} {label['informations']['music']}")
            failure = True
    else:
        results.append('')
        results.append('')
        results.append('')
        results.append('')
        results.append('')

    if label['details'] is not None and details is not None:
        recog_details = recog.get_details(details)

        graph = recog.get_graph(details)
        if 'display' in label['details'].keys():
            if graph == label['details']['display']:
                results.append('ok')
            else:
                results.append(f"{graph} {label['details']['display']}")
                failure = True
        else:
            results.append('none')

        recog_options = recog_details.options
        if recog_options is None:
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
            results.append('')
        else:
            if recog_options.arrange in define.value_list['options_arrange']:
                if recog_options.arrange == label['details']['option_arrange']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.arrange} {label['details']['option_arrange']}")
                    failure = True
            else:
                results.append('ok')
            
            if recog_options.arrange is not None and '/' in recog_options.arrange:
                if recog_options.arrange == label['details']['option_arrange_dp']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.arrange} {label['details']['option_arrange_dp']}")
                    failure = True
            else:
                results.append('ok')
            
            if recog_options.arrange in define.value_list['options_arrange_sync']:
                if recog_options.arrange == label['details']['option_arrange_sync']:
                    results.append('ok')
                else:
                    results.append(f"{recog_options.arrange} {label['details']['option_arrange_sync']}")
                    failure = True
            else:
                results.append('ok')
            
            if (recog_options.flip is None and label['details']['option_flip'] == '') or recog_options.flip == label['details']['option_flip']:
                results.append('ok')
            else:
                results.append(f"{recog_options.flip} {label['details']['option_flip']}")
                failure = True
            
            if (recog_options.assist is None and label['details']['option_assist'] == '') or recog_options.assist == label['details']['option_assist']:
                results.append('ok')
            else:
                results.append(f"{recog_options.assist} {label['details']['option_assist']}")
                failure = True
            
            if (recog_options.battle is None and label['details']['option_battle'] == '') or recog_options.battle == label['details']['option_battle']:
                results.append('ok')
            else:
                results.append(f"{recog_options.battle} {label['details']['option_battle']}")
                failure = True

        recog_clear_type = recog_details.clear_type
        recog_dj_level = recog_details.dj_level
        recog_score = recog_details.score
        recog_miss_count = recog_details.miss_count

        if (recog_clear_type.value is None and label['details']['clear_type'] == '') or recog_clear_type.value == label['details']['clear_type']:
            results.append('ok')
        else:
            results.append(f"{recog_clear_type.value} {label['details']['clear_type']}")
            failure = True

        if (recog_dj_level.value is None and label['details']['dj_level'] == '') or recog_dj_level.value == label['details']['dj_level']:
            results.append('ok')
        else:
            results.append(f"{recog_dj_level.value} {label['details']['dj_level']}")
            failure = True

        if (recog_score.value is None and label['details']['score'] == '') or recog_score.value == int(label['details']['score']):
            results.append('ok')
        else:
            results.append(f"{recog_score.value} {label['details']['score']}")
            failure = True

        if (recog_miss_count.value is None and label['details']['miss_count'] == '') or recog_miss_count.value == int(label['details']['miss_count']):
            results.append('ok')
        else:
            results.append(f"{recog_miss_count.value} {label['details']['miss_count']}")
            failure = True

        if recog_clear_type.new == label['details']['clear_type_new']:
            results.append('ok')
        else:
            results.append(f"{recog_clear_type.new} {label['details']['clear_type_new']}")
            failure = True
        
        if recog_dj_level.new == label['details']['dj_level_new']:
            results.append('ok')
        else:
            results.append(f"{recog_dj_level.new} {label['details']['dj_level_new']}")
            failure = True
        
        if recog_score.new == label['details']['score_new']:
            results.append('ok')
        else:
            results.append(f"{recog_score.new} {label['details']['score_new']}")
            failure = True
        
        if recog_miss_count.new == label['details']['miss_count_new']:
            results.append('ok')
        else:
            results.append(f"{recog_miss_count.new} {label['details']['miss_count_new']}")
            failure = True
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
        'notes',
        'music',
        'option_arrange',
        'option_arrange_dp',
        'option_arrange_sync',
        'option_flip',
        'option_assist',
        'option_battle',
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

        results = evaluate(filename, informations_image, details_image, key, label)

        output.append(f"{','.join(results)}\n")
    
    output.append(f'result, {not failure}')
    print(not failure)
    
    with open(result_filepath, 'w', encoding='utf-8') as f:
        f.writelines(output)
        f.close()
