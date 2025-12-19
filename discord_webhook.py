import json
import requests
from datetime import datetime

from result import Result,ResultInformations,ResultDetails

class DiscordwebhookModes():
    BATTLE: str = 'battle'
    SCORE: str = 'score'
    MISSCOUNT: str = 'misscount'

class DiscordwebhookStatuses():
    UPCOMING: str = 'upcoming'
    ONGOING: str = 'ongoing'
    ENDED: str = 'ended'

def post_test(url: str, values):
    if not values['private']:
        contexts = [f'{values['name']}']
    else:
        contexts = [f'{values['name']}(非公開)']

    contexts.append(f'開催者: {values['authorname']}')
    contexts.append(f'コメント: {values['comment']}')
    contexts.append(f'サイトURL: {values['siteurl']}')

    if values['mode'] == DiscordwebhookModes.BATTLE:
        contexts.append('モード: バトル')
    if values['mode'] == DiscordwebhookModes.SCORE:
        contexts.append('モード: スコア大会')
    if values['mode'] == DiscordwebhookModes.MISSCOUNT:
        contexts.append('モード: ミスカウント大会')

    if values['mode'] != DiscordwebhookModes.BATTLE:
        playmode = values['targetscore']['playmode']
        musicname = values['targetscore']['musicname']
        difficulty = values['targetscore']['difficulty']
        contexts.append(f'対象譜面: {musicname}[{playmode}{difficulty[0]}]')

    try:
        data = {'content': '\n'.join(contexts)}
        response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        if response.status_code != 204:
            return f'Error {response.status_code}'
    except Exception as ex:
        return (f'Error({len(ex.args)})', *ex.args)
    
    return None

def post_registered(url: str, id: str):
    contexts = [
        '登録が完了しました。',
        id
    ]

    try:
        data = {'content': '\n'.join(contexts)}
        requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    except Exception as ex:
        pass
    
def post_result(djname: str, nowdt: datetime, setting: dict, result: Result, imagevalue: bytes):
    informations: ResultInformations | None = result.informations
    details: ResultDetails | None = result.details

    if details is None or informations is None:
        return None, None

    contexts = [
        f'プレイヤー名: **{djname}**',
        f"日時: **{nowdt.strftime('%y/%m/%d %H:%M')}**",
    ]

    if setting['mode'] != DiscordwebhookModes.BATTLE:
        if setting['targetscore']['musicname'] != informations.music:
            return None, None
        if setting['targetscore']['playmode'] != informations.play_mode:
            return None, None
        if setting['targetscore']['difficulty'] != informations.difficulty:
            return None, None
        if details is None:
            return None, None
        if setting['mode'] == DiscordwebhookModes.SCORE:
            if details.score.current is None or setting['mybest'] is not None and setting['mybest'] >= details.score.current:
                return None, None
        if setting['mode'] == DiscordwebhookModes.MISSCOUNT:
            if details.miss_count.current is None or setting['mybest'] is not None and setting['mybest'] <= details.miss_count.current:
                return None, None
    
    if informations is not None:
        if not None in [informations.music, informations.play_mode, informations.difficulty]:
            contexts.append(f'**{informations.music}[{informations.play_mode}{informations.difficulty[0]}]**')
    
    if setting['mode'] != DiscordwebhookModes.MISSCOUNT:
        if details.score is not None and details.score.current is not None:
            contexts.append(f'SCORE: **{details.score.current}**')
    if setting['mode'] != DiscordwebhookModes.SCORE:
        if details.miss_count is not None and details.miss_count.current is not None:
            contexts.append(f'MISS COUNT: **{details.miss_count.current}**')
    if details.options is not None:
        option_arrange = details.options.arrange
        contexts.append(f'option: **{option_arrange if option_arrange is not None else "正規"}**')
    if informations.playspeed is not None:
        contexts.append(f'play speed: **{informations.playspeed}倍**')
    
    try:
        data = {'content': '\n'.join(contexts)}

        url = setting['posturl'] if 'posturl' in setting.keys() else setting['url']

        response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        if response.status_code != 204:
            return False, f'Error {response.status_code}'
        response = requests.post(url, files={'file': ('result.png', imagevalue)})
        if response.status_code != 200:
            return False, f'Error {response.status_code}'
    except Exception as ex:
            return False, (f'Error({len(ex.args)})', *ex.args)
    
    return True, 'Posted'

def post_leave(djname: str, setting: dict):
    try:
        data = {'content': f'**{djname}** は参加を辞退しました。'}

        url = setting['posturl'] if 'posturl' in setting.keys() else setting['url']

        response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        if response.status_code != 204:
            return False, f'Error {response.status_code}'
    except Exception as ex:
            return False, (f'Error({len(ex.args)})', *ex.args)
    