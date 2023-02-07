from resources import MusicsTimestamp,recog_musics_filepath
from storage import StorageAccessor

if __name__ == '__main__':
    storage = StorageAccessor()

    storage.upload_resource_musics(recog_musics_filepath)
    timestamp = str(storage.get_resource_musics_timestamp())

    musics_timestamp = MusicsTimestamp()
    musics_timestamp.write_timestamp(timestamp)
