import numpy as np
import pickle
from os import mkdir,remove
from os.path import join,exists,isfile
from PIL import Image
from glob import glob

from raw_image import raws_basepath
from larning import RawLabel,create_resource_directory
from resources import resources_dirname

error_output_count = 3
report_dirname = 'report'

class Report():
    log = []
    log_error = []
    count_through = 0
    count_error = 0
    count_errorvalue_save = 0

    def __init__(self, resourcename):
        if not exists(report_dirname):
            mkdir(report_dirname)
        
        self.report_dirpath = join(report_dirname, resourcename)
        for filepath in glob(join(self.report_dirpath, '*')):
            remove(filepath)
        if not exists(self.report_dirpath):
            mkdir(self.report_dirpath)
    
    def append_log(self, message):
        self.log.append(message)
    
    def through(self):
        self.count_through += 1
    
    def error(self, message):
        self.count_error += 1
        self.log_error.append(message)
    
    def saveimage_value(self, value, filename):
        image = Image.fromarray(value)
        image.save(join(self.report_dirpath, filename))

    def saveimage_errorvalue(self, value, filename):
        if self.count_errorvalue_save < error_output_count:
            image = Image.fromarray(value)
            image.save(join(self.report_dirpath, filename))
            self.count_errorvalue_save += 1
    
    def report(self):
        if self.count_error == 0:
            self.log.append('Complete')
            self.log.append(f'Through count: {self.count_through}')
        else:
            self.log.append(f'Error count: {self.count_through}')
        
        report_filepath = join(self.report_dirpath, 'report.txt')
        with open(report_filepath, 'w') as f:
            f.write('\n'.join(self.log))
            if len(self.log_error) > 0:
                f.write('Errors:')
                f.write('\n'.join(self.log_error))
        
        print('\n'.join(self.log))
        if len(self.log_error) > 0:
            print('Errors:')
            print('\n'.join(self.log_error[:error_output_count]))

class RawData():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_raws():
    labels = RawLabel()

    filenames = [*labels.all()]

    raws = {}
    for filename in filenames:
        filepath = join(raws_basepath, filename)
        if not isfile(filepath):
            continue

        label = labels.get(filename)
        if not 'screen' in label.keys():
            continue

        raws[filename] = RawData(np.array(Image.open(filepath).convert('RGB')), label)
    
    print(f"raw count: {len(raws)}")

    return raws

def get_report_dir(resource_name):
    if not exists(report_dirname):
        mkdir(report_dirname)
    
    report_dirpath = join(report_dirname, resource_name)
    for filepath in glob(join(report_dirpath, '*')):
        remove(filepath)
    if not exists(report_dirpath):
        mkdir(report_dirpath)
    
    return report_dirpath

def save_resource_serialized(resourcename, value):
    create_resource_directory()
    filepath = join(resources_dirname, resourcename)
    with open(filepath, 'wb') as f:
        pickle.dump(value, f)

def save_resource_numpy(resourcename, value):
    create_resource_directory()
    filepath = join(resources_dirname, resourcename)
    np.save(filepath, value)
