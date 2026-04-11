from logging import basicConfig,getLogger,DEBUG

basicConfig(
    level=DEBUG,
    filename='log.txt',
    filemode='w',
    format='%(asctime)s - %(name)s %(levelname)-7s %(message)s'
)

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from storage import StorageAccessor

dirpath = './collection_data/'

if __name__ == '__main__':
    storage = StorageAccessor()
    storage.download_and_delete_all(dirpath)
