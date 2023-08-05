from sys import argv
from os.path import join

from define import define
from resources import ResourceTimestamp,resources_dirname
from storage import StorageAccessor

def upload(filename, filepath):
    storage.upload_resource(filename, filepath)
    timestamp_str = storage.get_resource_timestamp(filename)

    timestamp = ResourceTimestamp(filename)
    timestamp.write_timestamp(timestamp_str)

    return True

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    storage = StorageAccessor()

    if '-all' in argv or '-informations' in argv:
        filename_informations = f'{define.informations_resourcename}.res'
        filepath_informations = join(resources_dirname, filename_informations)

        if upload(filename_informations, filepath_informations): 
            print(f'Upload complete {filename_informations}')

    if '-all' in argv or '-details' in argv:
        filename_details = f'{define.details_resourcename}.res'
        filepath_details = join(resources_dirname, filename_details)
        
        if upload(filename_details, filepath_details): 
            print(f'Upload complete {filename_details}')
    
    if '-all' in argv or '-musictable' in argv:
        filename_musictable = f'{define.musictable_resourcename}.res'
        filepath_musictable = join(resources_dirname, filename_musictable)
        
        if upload(filename_musictable, filepath_musictable): 
            print(f'Upload complete {filename_musictable}')
