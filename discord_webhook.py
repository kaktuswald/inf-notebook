import json
import requests

from result import Result,ResultInformations,ResultDetails

serversetting_default = {
    'settingname': None,
    'url': '',
    'mode': 'battle',
    'filter': 'none',
    'targetscore': None,
    'state': 'active',
    'mybest': None
}

def deactivate_allbattles(settings: dict):
    '''バトルモードの設定をすべてノンアクティブにする

    Args:
        settings(dict): 対象の設定リスト
    Returns:
        bool: 変更が有り
    '''
    changed = False

    for target in settings.values():
        if target['mode'] != 'battle':
            continue

        if target['state'] == 'active':
            target['state'] = 'nonactive'
            changed = True
    
    return changed

def post_result(djname: str, setting: dict, result: Result, imagevalue: bytes):
    informations: ResultInformations = result.informations
    details: ResultDetails = result.details

    if details is None:
        return None, None

    contexts = [f'DJ NAME: **{djname}**']

    if setting['mode'] != 'battle':
        if informations is None:
            return None, None
        if setting['targetscore']['musicname'] != informations.music:
            return None, None
        if setting['targetscore']['playmode'] != informations.play_mode:
            return None, None
        if setting['targetscore']['difficulty'] != informations.difficulty:
            return None, None
        if details is None:
            return None, None
        if setting['mode'] == 'score':
            if details.score.current is None or setting['mybest'] is not None and setting['mybest'] >= details.score.current:
                return None, None
        if setting['mode'] == 'misscount':
            if details.miss_count.current is None or setting['mybest'] is not None and setting['mybest'] <= details.miss_count.current:
                return None, None
    
    if informations is not None:
        if not None in [informations.music, informations.play_mode, informations.difficulty]:
            contexts.append(f'**{informations.music}[{informations.play_mode}{informations.difficulty[0]}]**')
    
    if setting['mode'] != 'misscount':
        if details.score is not None and details.score.current is not None:
            contexts.append(f'SCORE: **{details.score.current}**')
    if setting['mode'] != 'score':
        if details.miss_count is not None and details.miss_count.current is not None:
            contexts.append(f'MISS COUNT: **{details.miss_count.current}**')
    if details.options is not None:
        option_arrange = details.options.arrange
        contexts.append(f'option: **{option_arrange if option_arrange is not None else "正規"}**')
    
    try:
        data = {"content": '\n'.join(contexts)}
        response = requests.post(setting['url'], data=json.dumps(data), headers={"Content-Type": "application/json"})
        if response.status_code != 204:
            return False, f'Error {response.status_code}'
        response = requests.post(setting['url'], files={'file': ('result.png', imagevalue)})
        if response.status_code != 200:
            return False, f'Error {response.status_code}'
    except Exception as ex:
            return False, (f'Error({len(ex.args)})', *ex.args)
    
    return True, 'Posted'
