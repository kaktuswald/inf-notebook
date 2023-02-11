from datetime import datetime
import pyautogui as pgui
from PIL import Image,ImageGrab
from logging import getLogger
from os.path import exists,basename

logger_child_name = 'screenshot'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded screenshot.py')

from define import define
from resources import find_images
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

    def shot(self):
        self.image = ImageGrab.grab(all_screens=True)

    def find(self):
        key = define.searchscreen_keys[self.search_screen_keyindex]
        box =  pgui.locate(find_images[key], self.image, grayscale=True)
        if box is None:
            self.search_screen_keyindex = (self.search_screen_keyindex + 1) % len(define.searchscreen_keys)
            return False

        left = box.left - define.areas[key][0]
        top = box.top - define.areas[key][1]
        self.region = (
            left,
            top,
            left + self.width,
            top + self.height
        )
        self.region_loading = (
            left + define.areas['loading'][0],
            top + define.areas['loading'][1],
            left + define.areas['loading'][2],
            top + define.areas['loading'][3]
        )
        self.region_turntables = {}
        for key in define.areas['turntable'].keys():
            self.region_turntables[key] = (
                left + define.areas['turntable'][key][0],
                top + define.areas['turntable'][key][1],
                left + define.areas['turntable'][key][2],
                top + define.areas['turntable'][key][3]
            )
        self.region_result = (
            left + define.areas['result'][0],
            top + define.areas['result'][1],
            left + define.areas['result'][2],
            top + define.areas['result'][3]
        )

        return True

    @property
    def is_loading(self):
        return recog.get_is_screen_loading(self.image.crop(self.region_loading))

    @property
    def is_ended_waiting(self):
        for key in define.areas['turntable'].keys():
            if recog.get_is_screen_playing(self.image.crop(self.region_turntables[key])):
                return True
        return False

    def get(self):
        target = self.image
        if self.region is not None:
            target = target.crop(self.region)

        return target.convert('RGBA')

    def get_resultscreen(self):
        if not recog.get_is_screen_result(self.image.crop(self.region_result)):
            return None

        image = self.image.crop(self.region)
        original = image.convert('RGBA')
        monochrome = original.convert('L')

        if not recog.get_is_result(monochrome):
            return None

        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

        return Screen(original, monochrome, filename)

    def open(self, filepath):
        if not exists(filepath):
            return None
        
        image = Image.open(filepath)
        filename = basename(filepath)

        return Screen(image, image.convert('L'), filename)