from json import load,dump,loads,dumps
from os.path import join,exists,basename
from glob import glob
from PIL import Image
from base64 import b64encode
from numpy import array,uint8
from webui.webui import Window,Event,wait,clean

from resources_learning_musicselect import images_musicselect_basepath,label_filepath
from define import define,Playmodes
from general import get_imagevalue
from recog import Recognition as recog
from resources import resource

class GuiApi():
    window: Window

    @staticmethod
    def get_playmodes(event: Event):
        event.return_string(dumps(Playmodes.values))

    @staticmethod
    def get_versions(event: Event):
        event.return_string(dumps([*resource.musictable['versions'].keys()]))

    @staticmethod
    def get_difficulties(event: Event):
        event.return_string(dumps(define.value_list['difficulties']))

    @staticmethod
    def get_cleartypes(event: Event):
        event.return_string(dumps(define.value_list['clear_types']))

    @staticmethod
    def get_djlevels(event: Event):
        event.return_string(dumps(define.value_list['dj_levels']))

    @staticmethod
    def get_levels(event: Event):
        event.return_string(dumps(define.value_list['levels']))

    def __init__(self, window: Window):
        self.window = window
    
        window.bind('get_playmodes', GuiApi.get_playmodes)
        window.bind('get_versions', GuiApi.get_versions)
        window.bind('get_difficulties', GuiApi.get_difficulties)
        window.bind('get_cleartypes', GuiApi.get_cleartypes)
        window.bind('get_djlevels', GuiApi.get_djlevels)
        window.bind('get_levels', GuiApi.get_levels)

        window.bind('get_collectionkeys', self.get_collectionkeys)

        window.bind('get_images', self.get_images)
        window.bind('get_labels', self.get_labels)
        window.bind('get_recognitionresult', self.get_recognitionresult)
        window.bind('set_labels', self.set_labels)
    
    def get_collectionkeys(self, event: Event):
        conditions = loads(event.get_string_at(0))

        targetkeys = [*images.keys()]

        if conditions['only_notannotation']:
            targetkeys = [key for key in targetkeys if not key in labels.keys()]

        if conditions['only_undefinedmusicname'] or conditions['only_undefinedversion'] or conditions['musicnamefilter'] is not None:
            targetkeys = [key for key in targetkeys if key in labels.keys()]

        if conditions['only_undefinedmusicname']:
            targetkeys = [key for key in targetkeys if not 'musicname' in labels[key].keys() or labels[key]['musicname'] in [None, '']]

        if conditions['only_undefinedversion']:
            targetkeys = [key for key in targetkeys if not 'version' in labels[key].keys() or labels[key]['version'] in [None, '']]

        if conditions['only_ignore']:
            targetkeys = [key for key in targetkeys if key in labels.keys() and 'ignore' in labels[key].keys() and labels[key]['ignore']]

        if conditions['musicnamefilter'] is not None:
            targetkeys = [key for key in targetkeys if 'musicname' in labels[key].keys() and labels[key]['musicname'] is not None]
            targetkeys = [key for key in targetkeys if conditions['musicnamefilter'] in labels[key]['musicname']]

        if conditions['keyfilter'] is not None:
            targetkeys = [key for key in targetkeys if conditions['keyfilter'] in key]

        event.return_string(dumps(targetkeys))
    
    def get_images(self, event: Event):
        key = event.get_string_at(0)

        if images[key] is None:
            image = load_image(images_musicselect_basepath, key)

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
            'playmode': recog.MusicSelect.get_playmode(image_np),
            'version': recog.MusicSelect.get_version(image_np),
            'musicname': recog.MusicSelect.get_musicname(image_np),
            'difficulty': recog.MusicSelect.get_difficulty(image_np),
            'cleartype': recog.MusicSelect.get_cleartype(image_np),
            'djlevel': recog.MusicSelect.get_djlevel(image_np),
            'score': recog.MusicSelect.get_score(image_np),
            'misscount': recog.MusicSelect.get_misscount(image_np),
            'levels': recog.MusicSelect.get_levels(image_np),
        }

        event.return_string(dumps(result))

    def set_labels(self, event: Event):
        key = event.get_string_at(0)

        labels[key] = loads(event.get_string_at(1))

        with open(label_filepath, 'w') as f:
            dump(labels, f, indent=2)
    
images = {}
encodedimages = {}
labels = {}

def update_annotation():
    global labels

def load_image(basedir, key):
    filepath = join(basedir, key)

    if not exists(filepath):
        return None

    return Image.open(filepath)

if __name__ == '__main__':
    if exists(label_filepath):
        with open(label_filepath) as f:
            labels = load(f)
    
    for filepath in glob(join(images_musicselect_basepath, '*')):
        key = basename(filepath).removesuffix('.png')
        images[f'{key}.png'] = None

    window = Window()
    window.set_size(1150, 700)

    api = GuiApi(window)

    window.show('web_annotations/annotation_musicselect.html')

    wait()

    clean()
