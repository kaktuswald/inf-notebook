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

    if '-all' in argv or '-informations' in argv:
        filename_informations = f'{define.informations_resourcename}.res'
        filepath_informations = join(resources_dirname, filename_informations)
        
        storage.upload_resource(filename_informations, filepath_informations)
        timestamp = storage.get_resource_timestamp(filename_informations)

        timestamp_informations = ResourceTimestamp(filename_informations)
        timestamp_informations.write_timestamp(timestamp)

        print(f'Upload complete {filename_informations}')

    if '-all' in argv or '-details' in argv:
        filename_details = f'{define.details_resourcename}.json'
        filepath_details = join(resources_dirname, filename_details)
        
        storage.upload_resource(filename_details, filepath_details)
        timestamp = storage.get_resource_timestamp(filename_details)

        timestamp_details = ResourceTimestamp(filename_details)
        timestamp_details.write_timestamp(timestamp)
        
        print(f'Upload complete {filename_details}')

