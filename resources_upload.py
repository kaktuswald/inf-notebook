from sys import argv
from os.path import join
from json import load

from define import define
from resources import ResourceTimestamp,resources_dirname
from storage import StorageAccessor
from record import musicnamechanges_filename

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
    
    if '-all' in argv or '-musicselect' in argv:
        filename_musicselect = f'{define.musicselect_resourcename}.res'
        filepath_musicselect = join(resources_dirname, filename_musicselect)
        
        if upload(filename_musicselect, filepath_musicselect): 
            print(f'Upload complete {filename_musicselect}')
    
    if '-all' in argv or '-notesradar' in argv:
        filename_notesradar = f'{define.notesradar_resourcename}.res'
        filepath_notesradar = join(resources_dirname, filename_notesradar)
        
        if upload(filename_notesradar, filepath_notesradar): 
            print(f'Upload complete {filename_notesradar}')
    
    if '-all' in argv or '-musicnamechanges' in argv:
        filepath_musicnamechanges = join(resources_dirname, musicnamechanges_filename)

        try:
            with open(filepath_musicnamechanges, encoding='UTF-8')as f:
                convertlist = load(f)
            
            if upload(musicnamechanges_filename, filepath_musicnamechanges):
                print(f'Upload complete {musicnamechanges_filename}')
        except Exception as ex:
            print(f'Upload failed {musicnamechanges_filename}')
        
