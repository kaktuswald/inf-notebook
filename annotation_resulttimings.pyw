from json import load,dump,loads,dumps
from os import remove
from os.path import join,exists,basename,isfile
from glob import glob
from base64 import b64encode
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from numpy import array,uint8
from PIL import Image
from webui.webui import Window,Event,wait,clean

import data_collection as dc
from general import get_imagevalue
from recog import Recognition as recog
from windows import gethandle,maximize

windowtitle = 'タイミング画像のアノテーション'

class GuiApi():
    window: Window

    def __init__(self, window: Window):
        self.window = window
    
        window.bind('get_collectionkeys', self.get_collectionkeys)

        window.bind('get_images', self.get_images)
        window.bind('get_labels', self.get_labels)
        window.bind('get_recognitionresult', self.get_recognitionresult)
        window.bind('set_labels', self.set_labels)
        window.bind('delete_keyandlabel', self.delete_keyandlabel)
    
    def get_collectionkeys(self, event: Event):
        conditions = loads(event.get_string_at(0))

        targetkeys = [*images.keys()]

        if conditions['only_notannotation']:
            targetkeys = [key for key in targetkeys if not key in labels.keys()]
        else:
            if conditions['only_ignore']:
                targetkeys = [key for key in targetkeys if 'ignore' in labels[key].keys() and labels[key]['ignore']]

            if conditions['keyfilter'] is not None:
                targetkeys = [key for key in targetkeys if conditions['keyfilter'] in key]

        event.return_string(dumps(targetkeys))
    
    def get_images(self, event: Event):
        key = event.get_string_at(0)

        if images[key] is None:
            image = load_image(dc.images_resulttimings_basepath, key)

            images[key] = image

            decorded = None
            if image is not None:
                imagevalue = get_imagevalue(image)
                decorded = b64encode(imagevalue).decode('utf-8')

            encodedimages[key] = decorded

        event.return_string(dumps(encodedimages[key]))

    def get_labels(self, event: Event):
        key = event.get_string_at(0)

        if not key in labels.keys():
            event.return_string(dumps(None))
            return
        
        event.return_string(dumps(labels[key]))
    
    def get_recognitionresult(self, event: Event):
        key = event.get_string_at(0)

        image_np = array(images[key], dtype=uint8)
        result = {
            'fast': recog.Result.Timings.get_fast(image_np),
            'slow': recog.Result.Timings.get_slow(image_np),
        }

        event.return_string(dumps(result))

    def set_labels(self, event: Event):
        key = event.get_string_at(0)

        labels[key] = loads(event.get_string_at(1))

        self.save_labels()
    
    def delete_keyandlabel(self, event: Event):
        key = event.get_string_at(0)

        if key in labels.keys():
            del labels[key]
            self.save_labels()
        
        filepath = join(dc.images_resulttimings_basepath, key)
        if isfile(filepath):
            remove(filepath)
            del images[key]
    
    def save_labels(self):
        with open(dc.label_resulttimings_filepath, 'w') as f:
            dump(labels, f, indent=2)
    
images = {}
encodedimages = {}
labels = {}

def load_image(basedir, key):
    filepath = join(basedir, key)

    if not exists(filepath):
        return None

    return Image.open(filepath)

if __name__ == '__main__':
    if exists(dc.label_resulttimings_filepath):
        with open(dc.label_resulttimings_filepath) as f:
            labels = load(f)
    
    for filepath in glob(join(dc.images_resulttimings_basepath, '*')):
        key = basename(filepath).removesuffix('.png')
        images[f'{key}.png'] = None

    window = Window()
    window.set_size(1150, 700)

    api = GuiApi(window)

    window.show('web_manage/annotation_resulttimings.html')
    handle = gethandle(windowtitle)
    if handle:
        maximize(handle)

    wait()

    clean()
