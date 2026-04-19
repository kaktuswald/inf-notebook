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
            if not self.check_folder(ids['folderid']):
                ids['folderid'] = None
        
        if ids['folderid'] is None:
            result = self.create_folder()
            if result is None:
                return False
            
            ids['folderid'] = result['id']
        
        for key, filename in self.uploadtargets.items():
            filepath = export_dirpath.joinpath(filename)
            if filepath.is_file():
                result = self.upload_file(filepath, ids['folderid'], ids['fileids'][key])
                if result is not None:
                    ids['fileids'][key] = result['id'] if result is not None else None
        
        return True

    def check_folder(self, folderid=str):
        if self.service is None:
            self.service = build("drive", "v3", credentials=self.credentials)

        try:
            result = self.service.files().get(
                fileId=folderid,
            ).execute()
        except Exception as ex:
            logger.exception(ex)
            result = None

        logger.debug(result)
        return result

    def create_folder(self) -> dict:
        if self.service is None:
            self.service = build("drive", "v3", credentials=self.credentials)

        result = self.service.files().create(
            body={
                'name': productname,
                'mimeType': 'application/vnd.google-apps.folder',
            },
        ).execute()

        logger.debug(result)
        return result

    def upload_file(self, filepath:WindowsPath, folderid:str|None = None, fileid:str|None = None) -> dict:
        if self.service is None:
            self.service = build('drive', 'v3', credentials=self.credentials)

        media = MediaFileUpload(filepath, mimetype='text/plain')

        if fileid is not None:
            try:
                result = self.service.files().update(
                    fileId=fileid,
                    body={
                        'name': filepath.name,
                    },
                    media_body=media,
                ).execute()
            except Exception as ex:
                logger.exception(ex)
                fileid = None

        if fileid is None:
            try:
                result = self.service.files().create(
                    body={
                        'name': filepath.name,
                        'parents': [folderid],
                    },
                    media_body=media,
                ).execute()
            except Exception as ex:
                logger.exception(ex)
                result = None

        logger.debug(result)
        return result
