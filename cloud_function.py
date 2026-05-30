from json import dumps,loads
from uuid import uuid1
from requests import post
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
from pathlib import Path
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from google.auth.transport.requests import Request
from google.oauth2.service_account import IDTokenCredentials

from service_account_info import service_account_info

URLs = {
    'eventdelete': 'https://inf-notebook-eventdelete2-975441799295.asia-northeast2.run.app',
    'sendinquiry': 'https://inf-notebook-sendinquiry-975441799295.asia-northeast2.run.app',
}

def callfunction_eventdelete(filenames: list[str]):
    '''イベントファイルを削除する

    Args:
        filenames(list[str]): 削除するファイル名のリスト
    Returns:
        bool: 削除に成功
    '''
    url = URLs['eventdelete']

    credentials = IDTokenCredentials.from_service_account_info(service_account_info, target_audience=url)
    credentials.refresh(Request())

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {credentials.token}',
    }
    
    data = dumps({'filenames': filenames}).encode()

    response = post(url, headers=headers, data=data,)

    try:
        res = loads(response.text)
    except Exception as ex:
        logger.exception(ex)
        logger.info(response.text)
        return False
    
    if not isinstance(res, dict):
        return False
    
    if not 'success' in res.keys():
        return False
    
    return res['success']

def callfunction_sendinquiry(content: str, filepaths: list[str]):
    '''報告内容をアップロード

    Args:
        filepaths(list[str]): アップロードするファイルパスのリスト
    Returns:
        bool: アップロードに成功
    '''
    url = URLs['sendinquiry']
    
    credentials = IDTokenCredentials.from_service_account_info(service_account_info, target_audience=url)
    credentials.refresh(Request())

    headers = {
        'Authorization': f'Bearer {credentials.token}',
    }

    object_name = f'{uuid1()}.zip'
    
    files = {
        'file': (object_name, generate_zip(content, filepaths), 'application/zip')
    }

    response = post(url, headers=headers, files=files)

    try:
        res = loads(response.text)
    except Exception as ex:
        logger.exception(ex)
        logger.info(response.text)
        return False
    
    if not isinstance(res, dict):
        return False
    
    if not 'success' in res.keys():
        return False
    
    return res['success']

def generate_zip(content: str, filepaths: list[str]):
    zipdata = BytesIO()
    with ZipFile(zipdata, 'w', ZIP_DEFLATED) as zipfile:
        zipfile.writestr('content.txt', content.encode('utf-8'))

        for filepath in filepaths:
            path = Path(filepath)
            zipfile.write(path, arcname=path.name)
    zipdata.seek(0)

    return zipdata
