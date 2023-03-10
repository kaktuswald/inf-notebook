from datetime import datetime
from PIL import Image,ImageGrab
from logging import getLogger
from os.path import exists,basename

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define
from recog import recog

class Screen:
    def __init__(self, original, monochrome, filename):
        self.original = original
        self.monochrome = monochrome
        self.filename = filename

class Screenshot:
    width = 1280
    height = 720
    region = None
    search_screen_keyindex = 0

    def __init__(self, area):
        self.area = area
    
    def shot(self):
        self.image = ImageGrab.grab(all_screens=True, bbox=self.area)

    @property
    def is_loading(self):
        return recog.get_is_screen_loading(self.image.crop(define.areas['loading']))

    @property
    def is_ended_waiting(self):
        for key in define.areas['turntable'].keys():
            if recog.get_is_screen_playing(self.image.crop(define.areas['turntables'][key])):
                return True
        return False

    def get(self):
        target = self.image
        if self.region is not None:
            target = target.crop(self.region)

        return target.convert('RGBA')

    def get_resultscreen(self):
        if not recog.get_is_screen_result(self.image.crop(define.areas['result'])):
            return None

        original = self.image.convert('RGBA')
        monochrome = original.convert('L')

        if not recog.get_is_result(monochrome):
            return None

        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(original, monochrome, filename)

def open_screenimage(filepath):
    if not exists(filepath):
        return None
    
    image = Image.open(filepath)
    filename = basename(filepath)

    return Screen(image, image.convert('L'), filename)