from sys import argv
from os.path import join

from define import define
from resources import ResourceTimestamp,resources_dirname
from storage import StorageAccessor

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    storage = StorageAccessor()

    if '-all' in argv or '-musics' in argv:
        filename_musics = f'{define.musics_resourcename}.json'
        filepath_musics = join(resources_dirname, filename_musics)
        
        storage.upload_resource(filename_musics, filepath_musics)
        timestamp = storage.get_resource_timestamp(filename_musics)

        musics_timestamp = ResourceTimestamp(filename_musics)
        musics_timestamp.write_timestamp(timestamp)
        
        print(f'Upload complete {filename_musics}')

    if '-all' in argv or '-informations' in argv:
        filename_informations = f'{define.informations_resourcename}.res'
        filepath_informations = join(resources_dirname, filename_informations)
        
        storage.upload_resource(filename_informations, filepath_informations)
        timestamp = storage.get_resource_timestamp(filename_informations)

        musics_timestamp = ResourceTimestamp(filename_informations)
        musics_timestamp.write_timestamp(timestamp)

        print(f'Upload complete {filename_informations}')

