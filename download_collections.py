from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from storage import StorageAccessor

dirpath = './collection_data/'

if __name__ == '__main__':
    storage = StorageAccessor()
    storage.download_and_delete_all(dirpath)
