from pathlib import Path,WindowsPath
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource,build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from infnotebook import productname
from export import export_dirname
from googleapi_clientconfig import googleapi_clientconfig
from appdata import load_googleapi_credentials,save_googleapi_credentials,delete_googleapi_credentials

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]

export_dirpath = WindowsPath(Path.cwd()).joinpath(export_dirname)

class GoogleApiAccesor():
    credentials: Credentials|None = None
    service: Resource|None = None

    uploadtargets = {
        'fileid_csv_sp': 'SP.csv',
        'fileid_csv_dp': 'DP.csv',
        'fileid_csv_dpbattle': 'DP BATTLE.csv',
    }

    def __init__(self):
        userinfo = load_googleapi_credentials()
        if userinfo is not None:
            self.credentials = Credentials.from_authorized_user_info(userinfo)

    def get_credentials(self) -> bool:
        try:
            flow = InstalledAppFlow.from_client_config(googleapi_clientconfig, SCOPES)
            self.credentials = flow.run_local_server(port=0, timeout_seconds=60)

            save_googleapi_credentials(self.credentials.to_json())

            return True
        except Exception as ex:
            logger.exception(ex)
        
        return False

    def delete_credentialsfile(self) -> bool:
        if self.credentials is None:
            return False
        
        if delete_googleapi_credentials():
            if self.service is not None:
                self.service.close()
                self.service = None
            self.credentials = None
        
        return True
    
    def upload_googledrive(self, ids:dict) -> bool:
        if self.credentials is None:
            return False
        
        if ids['folderid'] is not None:
            if not self.check_file(ids['folderid']):
                ids['folderid'] = None
                for key in ids['fileids']:
                    ids['fileids'][key] = None
        
        if ids['folderid'] is None:
            ids['folderid'] = self.create_folder()
        
        for key, filename in self.uploadtargets.items():
            filepath = export_dirpath.joinpath(filename)
            if not filepath.is_file():
                continue

            if ids['fileids'][key]:
                if self.check_file(ids['fileids'][key]):
                    self.update_file(filepath, ids['fileids'][key])
                else:
                    ids['fileids'][key] = None
            
            if ids['fileids'][key] is None:
                ids['fileids'][key] = self.create_file(filepath, ids['folderid'])
        
        return True

    def check_file(self, fileid=str) -> bool:
        if self.service is None:
            self.service = build("drive", "v3", credentials=self.credentials)

        try:
            result = self.service.files().get(
                fileId=fileid,
                fields='id,trashed',
            ).execute()
        except HttpError as ex:
            logger.exception(ex.reason)
            return False
        except Exception as ex:
            logger.exception(ex)
            return False

        return not result['trashed']

    def create_folder(self) -> str|None:
        if self.service is None:
            self.service = build("drive", "v3", credentials=self.credentials)

        result = self.service.files().create(
            body={
                'name': productname,
                'mimeType': 'application/vnd.google-apps.folder',
            },
            fields='id',
        ).execute()

        logger.debug(result)
        return result['id']

    def create_file(self, filepath:WindowsPath, folderid:str) -> str|None:
        if self.service is None:
            self.service = build('drive', 'v3', credentials=self.credentials)

        media = MediaFileUpload(filepath, mimetype='text/plain')

        try:
            result = self.service.files().create(
                body={
                    'name': filepath.name,
                    'parents': [folderid],
                },
                media_body=media,
                fields='id',
            ).execute()
        except HttpError as ex:
            logger.exception(ex.reason)
            result = None
        except Exception as ex:
            logger.exception(ex)
            result = None

        logger.debug(result)
        return result['id']
    
    def update_file(self, filepath:WindowsPath, fileid:str|None = None) -> bool:
        if self.service is None:
            self.service = build('drive', 'v3', credentials=self.credentials)

        media = MediaFileUpload(filepath, mimetype='text/plain')

        try:
            self.service.files().update(
                fileId=fileid,
                media_body=media,
                fields='id',
            ).execute()
        except HttpError as ex:
            logger.exception(ex.reason)
            return False
        except Exception as ex:
            logger.exception(ex)
            return False

        return True
    
    def __del__(self):
        if self.service is not None:
            self.service.close()
