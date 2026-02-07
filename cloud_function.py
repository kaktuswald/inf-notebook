from json import dumps,loads
from requests import post
from google.auth.transport.requests import Request
from google.oauth2.service_account import IDTokenCredentials
from logging import getLogger

logger = getLogger('cloud function')

from service_account_info import service_account_info

URL = 'https://inf-notebook-eventdelete2-975441799295.asia-northeast2.run.app'

def callfunction_eventdelete(filenames: list[str]):
    """イベントファイルを削除する

    Args:
        filenames(list[str]): 削除するファイル名のリスト
    Returns:
        bool: 削除に成功
    """
    credentials = IDTokenCredentials.from_service_account_info(service_account_info, target_audience=URL)
    credentials.refresh(Request())

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {credentials.token}',
    }
    
    data = dumps({'filenames': filenames}).encode()

    response = post(URL, headers=headers, data=data,)

    try:
        res = loads(response.text)
    except Exception as ex:
        logger.exception(ex)
        return False
    
    if not isinstance(res, dict):
        return False
    
    if not 'success' in res.keys():
        return False
    
    return res['success']
