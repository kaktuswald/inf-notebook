import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename='log.txt',
    filemode='w',
    format='%(asctime)s - %(name)s %(levelname)-7s %(message)s'
)

logger = logging.getLogger()

logger.debug('loaded download.py')

from storage import StorageAccessor

dirpath = './collection_data/'

if __name__ == '__main__':
    storage = StorageAccessor()
    storage.download_and_delete_all(dirpath)
