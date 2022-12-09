from storage import StorageAccessor

dirpath = './collection_data/'

if __name__ == '__main__':
    storage = StorageAccessor()
    storage.download_and_delete_all(dirpath)
