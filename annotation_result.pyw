from json import load,dump,loads,dumps
from os.path import join,exists,basename
from glob import glob
from PIL import Image
from base64 import b64encode
from numpy import array,zeros,uint8
from webui.webui import Window,Event,wait,clean

import data_collection as dc
from define import define,Playmodes,Graphtypes
from general import get_imagevalue
from recog import Recognition as recog

class GuiApi():
    window: Window

    @staticmethod
    def get_playmodes(event: Event):
        event.return_string(dumps(Playmodes.values))

    @staticmethod
    def get_difficulties(event: Event):
        event.return_string(dumps(define.value_list['difficulties']))

    @staticmethod
    def get_levels(event: Event):
        event.return_string(dumps(define.value_list['levels']))

    @staticmethod
    def get_graphtypes(event: Event):
        event.return_string(dumps(Graphtypes.values))

    @staticmethod
    def get_options(event: Event):
        event.return_string(dumps({
            'arrange': define.value_list['options_arrange'],
            'arrange_dp': define.value_list['options_arrange_dp'],
            'arrange_sync': define.value_list['options_arrange_sync'],
            'flip': define.value_list['options_flip'],
            'assist': define.value_list['options_assist'],
        }))

    @staticmethod
    def get_cleartypes(event: Event):
        event.return_string(dumps(define.value_list['clear_types']))

    @staticmethod
    def get_djlevels(event: Event):
        event.return_string(dumps(define.value_list['dj_levels']))

    @staticmethod
    def get_graphtargets(event: Event):
        event.return_string(dumps(define.value_list['graphtargets']))

    def __init__(self, window: Window):
        self.window = window
    
        window.bind('get_playmodes', GuiApi.get_playmodes)
        window.bind('get_difficulties', GuiApi.get_difficulties)
        window.bind('get_levels', GuiApi.get_levels)
        window.bind('get_graphtypes', GuiApi.get_graphtypes)
        window.bind('get_options', GuiApi.get_options)
        window.bind('get_cleartypes', GuiApi.get_cleartypes)
        window.bind('get_djlevels', GuiApi.get_djlevels)
        window.bind('get_graphtargets', GuiApi.get_graphtargets)

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

        if conditions['only_undefinedmusicname'] or conditions['only_fullcombo'] or conditions['musicnamefilter'] is not None:
            targetkeys = [key for key in targetkeys if key in labels.keys()]

        if conditions['only_undefinedmusicname'] or conditions['musicnamefilter'] is not None:
            targetkeys = [key for key in targetkeys if 'informations' in labels[key].keys() and labels[key]['informations'] is not None]

        if conditions['only_undefinedmusicname']:
            targetkeys = [key for key in targetkeys if not 'music' in labels[key]['informations'].keys() or labels[key]['informations']['music'] in [None, '']]

        if conditions['only_ignore']:
            targetkeys = [key for key in targetkeys if key in labels.keys() and 'ignore' in labels[key].keys() and labels[key]['ignore']]

        if conditions['only_fullcombo']:
            targetkeys = [key for key in targetkeys if 'details' in labels[key].keys() and labels[key]['details'] is not None]
            targetkeys = [key for key in targetkeys if ('clear_type_best' in labels[key]['details'].keys() and labels[key]['details']['clear_type_best'] == 'F-COMBO') or ('clear_type_current' in labels[key]['details'].keys() and labels[key]['details']['clear_type_current'] == 'F-COMBO')]

        if conditions['musicnamefilter'] is not None:
            targetkeys = [key for key in targetkeys if 'music' in labels[key]['informations'].keys() and labels[key]['informations']['music'] is not None]
            targetkeys = [key for key in targetkeys if conditions['musicnamefilter'] in labels[key]['informations']['music']]

        if conditions['keyfilter'] is not None:
            targetkeys = [key for key in targetkeys if conditions['keyfilter'] in key]

        event.return_string(dumps(targetkeys))
    
    def get_images(self, event: Event):
        key = event.get_string_at(0)

        if images[key] is None:
            image_informations = load_image(dc.informations_basepath, key)
            image_details = load_image(dc.details_basepath, key)

            images[key] = {
                'informations': image_informations,
                'details': image_details,
            }

            decorded_informations = None
            if image_informations is not None:
                imagevalue_informations = get_imagevalue(image_informations)
                decorded_informations = b64encode(imagevalue_informations).decode('utf-8')

            decorded_details = None
            if image_details is not None:
                imagevalue_details = get_imagevalue(image_details)
                decorded_details = b64encode(imagevalue_details).decode('utf-8')

            encodedimages[key] = {
                'informations': decorded_informations,
                'details': decorded_details,
            }

        event.return_string(dumps(encodedimages[key]))

    def get_labels(self, event: Event):
        key = event.get_string_at(0)

        if not key in labels.keys():
            event.return_string(dumps(None))
            return
        
        event.return_string(dumps(labels[key]))
    
    def get_recognitionresult(self, event: Event):
        key = event.get_string_at(0)

        informations = None
        if images[key]['informations'] is not None:
            informationimage = images[key]['informations']
            np_value = zeros((define.informations_trimsize[1], define.informations_trimsize[0], 3))
            np_value[define.informations_trimsize[1] - informationimage.height:, :, :] = array(informationimage, dtype=uint8)
            result = recog.Result.get_informations(np_value)
            informations = {
                'playmode': result.play_mode,
                'difficulty': result.difficulty,
                'level': result.level,
                'notes': result.notes,
                'musicname': result.music,
            }

        details = None
        if images[key]['details'] is not None:
            result = recog.Result.get_details(array(images[key]['details'], dtype=uint8))
            details = {
                'graphtype': result.graphtype,
                'optionbattle': result.options.battle if result.options is not None else None,
                'optionarrange': result.options.arrange if result.options is not None else None,
                'optionflip': result.options.flip if result.options is not None else None,
                'optionassist': result.options.assist if result.options is not None else None,
                'cleartypebest': result.clear_type.best,
                'cleartypecurrent': result.clear_type.current,
                'cleartypenew': result.clear_type.new,
                'djlevelbest': result.dj_level.best,
                'djlevelcurrent': result.dj_level.current,
                'djlevelnew': result.dj_level.new,
                'scorebest': result.score.best,
                'scorecurrent': result.score.current,
                'scorenew': result.score.new,
                'misscountbest': result.miss_count.best,
                'misscountcurrent': result.miss_count.current,
                'misscountnew': result.miss_count.new,
                'graphtarget': result.graphtarget,
            }

        event.return_string(dumps({'informations': informations, 'details': details}))

    def set_labels(self, event: Event):
        key = event.get_string_at(0)

        labels[key] = loads(event.get_string_at(1))

        with open(dc.label_filepath, 'w') as f:
            dump(labels, f, indent=2)
    
images = {}
encodedimages = {}
labels = {}

def update_annotation():
    global labels

def load_image(basedir, key):
    filename = f'{key}.png'
    filepath = join(basedir, filename)

    if not exists(filepath):
        return None

    return Image.open(filepath)

if __name__ == '__main__':
    if exists(dc.label_filepath):
        with open(dc.label_filepath) as f:
            labels = load(f)
    
    for filepath in glob(join(dc.informations_basepath, '*')):
        key = basename(filepath).removesuffix('.png')
        images[key] = None
    for filepath in glob(join(dc.details_basepath, '*')):
        key = basename(filepath).removesuffix('.png')
        images[key] = None

    window = Window()
    window.set_size(1150, 700)

    api = GuiApi(window)

    window.show('web_annotations/annotation_result.html')

    wait()

    clean()
