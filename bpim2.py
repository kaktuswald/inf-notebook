import requests
from requests.exceptions import HTTPError
from time import time
from datetime import datetime
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from appdata import Bpim2ChartBpiCache

BASE_URL: str = 'https://bpi2.poyashi.me/api/v1'
FIREBASE_WEB_API_KEY: str = None
API_KEY: str = None

REREQUEST_MINSPAN: int = 2 * 60 * 60 * 24
'''前回リクエストからの再リクエストの最小スパン(秒)
'''

CACHESAVE_MINSPAN: float = 10 * 60
'''キャッシュファイル保存の最小スパン(秒)
'''

chartbpicache: dict[str, dict[str, dict[str, datetime|int|float]|None]] = Bpim2ChartBpiCache.load() or {}
cachesaved_datetime: float|None = None
callcount: int = 0

def bpim2_getchartbpi(songname:str, difficulty:str, score:int) -> float:
    global cachesaved_datetime
    global callcount

    nowdt = datetime.now()

    shouldrequest = not chartbpicache.get(songname)
    if not shouldrequest:
        shouldrequest = not chartbpicache[songname].get(difficulty)
        if not shouldrequest:
            shouldrequest = any([
                chartbpicache[songname][difficulty]['score'] > score,
                (nowdt - chartbpicache[songname][difficulty]['dt']).seconds > REREQUEST_MINSPAN,
            ])
    
    if shouldrequest:
        if not songname in chartbpicache.keys():
            chartbpicache[songname] = {}
        
        result = calculate_bpi(songname, difficulty, score)
        bpi = result['bpi'] if result else None
        callcount += 1
        nowtime = time()

        chartbpicache[songname][difficulty] = {
            'dt': nowdt,
            'score': score,
            'bpi': bpi,
        }

        if cachesaved_datetime is None or nowtime - cachesaved_datetime > CACHESAVE_MINSPAN:
            Bpim2ChartBpiCache.save(chartbpicache)
            cachesaved_datetime = nowtime
            logger.debug(f'saved bpim2 chartbpi cache: {nowdt}')

        return bpi

    if not difficulty in chartbpicache[songname].keys():
        return None
    
    return  chartbpicache[songname][difficulty]['bpi']

def bpim2_savecache():
    Bpim2ChartBpiCache.save(chartbpicache)
    logger.debug('saved bpim2 chartbpi cache')

def bpim2_getcallcount():
    return callcount

def api_request(path:str, id_token:str|None=None, **kwargs):
    if id_token:
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {id_token}'
        res = requests.get(f'{BASE_URL}{path}', headers=headers, **kwargs)
    else:
        res = requests.get(f'{BASE_URL}{path}', **kwargs)

    try:
        res.raise_for_status()
    except HTTPError as ex:
        logger.exception(ex)
        return None

    return res.json()

def get_id_token() -> str|None:
    '''IDトークンを取得
    '''
    if not API_KEY or not FIREBASE_WEB_API_KEY:
        return None

    res = requests.post(
        f'{BASE_URL}/token',
        headers={'X-Api-Key': API_KEY}
    )

    try:
        res.raise_for_status()
    except HTTPError as ex:
        logger.exception(ex)
        return None
    
    custom_token = res.json()['customToken']

    res = requests.post(
        f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken',
        params={'key': FIREBASE_WEB_API_KEY},
        json={'token': custom_token, 'returnSecureToken': True}
    )

    try:
        res.raise_for_status()
    except HTTPError as ex:
        logger.exception(ex)
        return None

    return res.json()['idToken']

def get_me(id_token:str):
    '''ログインユーザー情報取得
    '''
    result = api_request('/me', id_token)
    
    return result

def get_scores(id_token:str, userid:str):
    '''指定日時のスコア一覧取得
    '''
    result = api_request(
        f'/users/{userid}/scores',
        id_token,
        params={'version': '33'},
    )

    return result

def get_allscores(id_token:str, userid:str):
    '''全難易度スコア一覧取得
    '''
    result = api_request(
        f'/users/{userid}/all-scores/list',
        id_token,
        params={'sortKey': 'bpi'}
    )

    return result

def get_totalbpihistory(id_token:str, userid:str, version:str):
    '''TotalBPIの日別推移取得
    '''
    result = api_request(
        f'/users/{userid}/stats/totalBPIhistory',
        id_token,
        params={'version': version}
    )

    return result

def get_singlebpidistribution(id_token:str, userid:str):
    '''楽曲別BPI分布取得
    '''
    result = api_request(
        f'/users/{userid}/stats/singleBPIDistribution',
        id_token,
        params={'version': '33', 'sortKey': 'bpi'}
    )

    return result

def calculate_bpi(songname:str, difficulty:str, score:int) -> dict:
    result = api_request(
        f'/bpi/calc',
        params={'title': songname, 'difficulty': difficulty, 'exScore': score}
    )

    if result:
        logger.debug(f'calculated {songname} {difficulty}: {result["bpi"]}')

    return result

